from typing import Union, Tuple, List, Any
import numpy as np

from wrapper.config.config_builder import load_config
from wrapper.core.data_management import MtutManager
from wrapper.misc.lin_alg import line_coefficients


def retrieve_current_value(currents_string: str) -> Union[float, None]:
    """
    Prepare raw "Treada's" output string to following operations.

    :param currents_string: raw "Treada's" output string
    :return: source current value (from first column of "Treada's" output)
    """
    currents_list = currents_string.split(' ')
    length_current_list = len(currents_list)
    if length_current_list == 12 or length_current_list == 13:
        try:
            float(currents_list[3])
            return float(currents_list[0])
        except ValueError:
            return None


class EndingCondition:
    """
    Describe the logic of ending condition to stop "Treada's" work stage.
    """
    def __init__(self, chunk_size: int, equal_values_to_stop: int, deviation_coef: float):
        # Chunk vector init
        self.chunk: np.ndarray = np.zeros(chunk_size)
        self.chunk_size = chunk_size
        self.chunk_index = 0
        # Vector of mean values of each chunk init
        self.chunks_means_vector = np.zeros(equal_values_to_stop)
        self.means_vector_index = 0
        self.equal_values_to_stop = equal_values_to_stop
        self.deviation_coef = deviation_coef

    @staticmethod
    def is_equal(vector: np.ndarray, deviation: float) -> bool:
        """
        Check is all elements of vector lie in range of deviation.

        :param vector:
        :param deviation:
        :return:
        """
        difference = np.ptp(vector)
        if difference < 2*deviation:
            print(f'{difference=}')
            print(f'{2*deviation=}')
            return True
        elif np.amax(np.abs(vector)) < 10e-11:
            print('Stopped by null condition.')
            return True
        else:
            return False

    def deviation(self):
        max_abs_mean = np.amax(np.abs(self.chunks_means_vector))
        deviation = max_abs_mean * self.deviation_coef
        return deviation

    def check(self, source_current: float, **kwargs) -> bool:
        """
        Checks ending condition.

        :param source_current: source current value (from first column of "Treada's" output)
        :return: True if condition is satisfied, False if it is not.
        """
        if self.chunk_index < self.chunk.size:
            self.chunk[self.chunk_index] = source_current
            self.chunk_index += 1
        else:
            self.chunk_index = 0
            self.chunks_means_vector[self.means_vector_index] = np.mean(self.chunk)

            if self.means_vector_index >= self.chunks_means_vector.size - 1:
                deviation_value = self.deviation()
                if self.is_equal(self.chunks_means_vector, deviation_value):
                    return True
                else:
                    self.chunks_means_vector = np.roll(self.chunks_means_vector, shift=-1)
                    self.means_vector_index -= 1
            else:
                self.means_vector_index += 1
        return False


class Chunk:
    def __init__(self, low_index: int, size: int):
        self.size = size
        self.storage = np.zeros(size)
        self._index = 0
        self.low_index = low_index
        self.high_index = self.low_index + self.size
        self.x = 0.
        self.y = 0.

    def is_full(self):
        if self._index < self.size:
            return False
        else:
            return True

    def append(self, new_value):
        self.storage[self._index] = new_value
        self._index += 1
        if self.is_full():
            self._index = 0

    def get_mean_current(self) -> Union[float, None]:
        if np.any(self.storage != 0):
            return np.mean(self.storage)
        else:
            return None

    def set_y(self, y: float):
        if y:
            self.y = y

    def get_mean_index(self):
        return int((self.high_index + self.low_index) / 2)

    def __repr__(self):
        class_name = self.__class__.__name__
        return f'{class_name}: low_index={self.low_index} high_index={self.high_index} size={self.size}'


class ChunkSmall(Chunk):
    step: int


class ChunkBig(Chunk):
    step: int


class StepBasedEndingCondition:
    def __init__(self,
                 precision: float
                 , chunk_size: int,
                 big_step_multiplier=1000,
                 low_step_border=500.,
                 high_step_border=10e5,):
        self.precision = precision
        self.treada_time_step = self._get_treada_time_step()

        self.low_step_border = low_step_border
        self.high_step_border = high_step_border

        small_step, big_step = self._calculate_steps(big_step_multiplier=big_step_multiplier)
        self.steps_ratio = 2

        ChunkSmall.step = small_step
        ping_pong_small = [
            ChunkSmall(0, chunk_size),
            ChunkSmall(small_step + chunk_size, chunk_size)
        ]

        ChunkBig.step = big_step
        ping_pong_big = [
            ChunkBig(0, chunk_size),
            ChunkBig(big_step + chunk_size, chunk_size)
        ]
        self.ping_pong = [ping_pong_small, ping_pong_big]

        self.step_scale = 1 / 30

    @staticmethod
    def _get_treada_time_step() -> float:
        config = load_config('config.json')
        mtut_manager = MtutManager(config.paths.treada_core.mtut)
        mtut_manager.load_file()
        treada_time_step_str = mtut_manager.get_var('TSTEP')
        return float(treada_time_step_str)

    def _calculate_steps(self, big_step_multiplier: float,
                         small_step_multiplier=0,
                         index_dependent_step_multiplier=1) -> Tuple[int, int]:
        if small_step_multiplier < big_step_multiplier:
            # Steps that depend on treada time step are calculated here
            initial_step_coef = np.abs(np.log10(self.treada_time_step))
            big_step = initial_step_coef * big_step_multiplier * index_dependent_step_multiplier
            if not small_step_multiplier:
                small_step = big_step / 2
            else:
                small_step = initial_step_coef * small_step_multiplier * index_dependent_step_multiplier

            self.steps_ratio = big_step / small_step
            # If steps go out of defined borders, returns them into that
            if small_step < self.low_step_border:
                small_step = self.low_step_border
                big_step = small_step * self.steps_ratio
            if big_step > self.high_step_border:
                big_step = self.high_step_border
                small_step = big_step / self.steps_ratio

            print(f'{small_step=} {big_step=}')
            return round(small_step), round(big_step)
        else:
            raise ValueError('small_step_multiplier can not exceed big_step_multiplier')

    def update_steps_scale(self, current_index: int):
        if current_index > 2000 and ChunkBig.step / current_index < self.step_scale:
            ChunkBig.step = int(current_index * self.step_scale)
            ChunkSmall.step = int(ChunkBig.step / self.steps_ratio)



    @staticmethod
    def swap_chunks():
        pass

    def check(self,  current_index: int, source_current: float) -> bool:
        """
        Must be redefined by child class.
        :param current_index: Line with currents index that read from Treada output.
        :param source_current: Current value that read from Treada output.
        :return: True if condition is satisfied and False if not.
        """
        pass


class LineEndingCondition(StepBasedEndingCondition):
    def __init__(self,
                 precision: float,
                 chunk_size: int,
                 big_step_multiplier=1000,
                 low_step_border=500.,
                 high_step_border=10e5,):
        super(LineEndingCondition, self).__init__(precision, chunk_size, big_step_multiplier, low_step_border,
                                                  high_step_border)

    def check(self,  current_index: int, source_current: float) -> bool:
        # print(f'{current_index=}')

        for chunks in self.ping_pong:
            if chunks[1].low_index <= current_index < chunks[1].high_index:
                chunks[1].append(source_current)
                # print(f'{chunks[1]=}')
            elif current_index == chunks[1].high_index:
                for chunk in chunks:
                    chunk.x = chunk.get_mean_index()
                    chunk.set_y(chunk.get_mean_current())
                # print(f'{chunks[0].x=} {chunks[0].y=}')
                # print(f'{chunks[1].x=} {chunks[1].y=}')

                # print(f'{self.ping_pong=}')

                k, _ = line_coefficients(first_point_coords=[chunks[0].x, chunks[0].y * 1e3],
                                         second_point_coords=[chunks[1].x, chunks[1].y * 1e3])
                chunks[1].k = k
                if np.abs(k) < self.precision:
                    return True
                chunks[0], chunks[1] = chunks[1], chunks[0]
                chunks[1].low_index = chunks[0].high_index + chunks[0].step
                chunks[1].high_index = chunks[1].low_index + chunks[1].size
        return False


class MeansEndingCondition(StepBasedEndingCondition):
    def __init__(self,
                 precision: float,
                 chunk_size: int,
                 big_step_multiplier=1000,
                 low_step_border=500.,
                 high_step_border=10e5,):
        super(MeansEndingCondition, self).__init__(precision, chunk_size, big_step_multiplier, low_step_border,
                                                   high_step_border)
        self.max_current = None
        self.min_current = None
        self.current_scale = None

        self.condition_requirements = [False, False]

    def init_extremes(self, new_point: float):
        self.max_current = self.min_current = new_point

    def update_scale(self, new_point: float):
        is_updated = False
        if new_point:
            if new_point > self.max_current:
                self.max_current = new_point
                is_updated = True
            elif new_point < self.min_current:
                self.min_current = new_point
                is_updated = True
            if is_updated:
                self.current_scale = np.abs(self.max_current - self.min_current)

    def deviation(self) -> float:
        if self.current_scale:
            deviation = self.current_scale * self.precision
        else:
            deviation = self.precision
        return deviation

    def is_equal(self, prev_mean_current: float, next_mean_current: float) -> bool:
        deviation = self.deviation()
        if np.abs(next_mean_current - prev_mean_current) < deviation:
            return True
        else:
            return False

    def update_condition_requirements(self, condition_result, index):
        self.condition_requirements[index] = condition_result

    def check(self,  current_index: int, source_current: float):
        # print(f'{current_index=}')

        if not self.current_scale:
            self.init_extremes(source_current)

        for kind_index, chunks in enumerate(self.ping_pong):
            if chunks[1].low_index <= current_index < chunks[1].high_index:
                chunks[1].append(source_current)
                # print(f'{chunks[1]=}')
            elif current_index == chunks[1].high_index:
                for chunk in chunks:
                    chunk.x = chunk.get_mean_index()
                    chunk.set_y(chunk.get_mean_current())
                    self.update_scale(chunk.y)
                # print(f'{chunks[0].x=} {chunks[0].y=}')
                # print(f'{chunks[1].x=} {chunks[1].y=}')

                # print(f'{self.ping_pong=}')

                if self.is_equal(chunks[0].y, chunks[1].y):
                    self.condition_requirements[kind_index] = True

                chunks[0], chunks[1] = chunks[1], chunks[0]
                chunks[1].low_index = chunks[0].high_index + chunks[0].step
                chunks[1].high_index = chunks[1].low_index + chunks[1].size

        self.update_steps_scale(current_index)

        if False not in self.condition_requirements:
            return True
        return False


if __name__ == '__main__':
    cdn = StepBasedEndingCondition(10, 1)
    print(f'{cdn.ping_pong=}')
    chunk = Chunk(5, 3)
    print(chunk.low_index)
    print(chunk.high_index)
    print(chunk.get_mean_index())

