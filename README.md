# Treada Launcher

## 1. Description
This program is designed to calculate the response time of a semiconductor device to a light pulse.

## 2. Installation
1. Place the `treada-launcher/` folder with all its contents in any convenient directory on your computer.
2. Navigate to the directory `treada-launcher/installer_x64/` and run `installer.bat` as an administrator.  
   This will install Python (if not already installed) and all necessary dependencies.
3. Rename the file `wrapper/config/config.json.example` to `wrapper/config/config.json`.  
   (It is recommended to save a copy of the original `config.json.example` file beforehand.)
4. If dependency installation fails for any reason:  
   a) Restart `installer.bat` from the command prompt (cmd) launched with administrator privileges, specifying the full path to `installer.bat`.  
   b) If this does not help, ensure your internet connection is active and rerun `installer.bat`.

Critical errors during installation are logged in the `requirements_installer.log` file.  
For installation and usage inquiries, contact: alex.bringold@gmail.com

## 3. Basic Operation - Calculating Response Time of a Semiconductor Device to a Light Pulse
### Initial Variable Values:
- `CKLKRS` = 1 and `ILUMEN` = 0  
These values in the "MTUT" file will be set automatically. During the calculation step "with light," the necessary values of these variables will also be set automatically.

1. Specify all required calculation variables (except those mentioned above) in the "MTUT" file.  
   The "MTUT" file, along with other necessary files for the execution of `TreadaTx_C.exe`, is located in the `TreadaTx_C\` directory.
2. To start the program, open the command prompt, navigate to the root project directory (`treada-launcher/`), and use the command:  
   `py treada_launcher.py`
3. Monitor the completion of the transient process using the source current values (first column of program output) and press `Ctrl + C` to proceed to the second calculation step.
4. Monitor the transient process completion at step 2 as in step 3. Then press `Ctrl + C` again.

### Results:
- A brief report will appear in the command prompt, including input parameters and transient time.
- Calculation results, including input data and current density vs. time dependency, will be saved in the `data\` directory.  
  The file name will be: `res_u(<UDRM Value from MTUT>).txt`.  
  A transient process plot for the "with light" mode will also be generated.
5. To terminate the program completely, press `Ctrl + C` one more time in the command prompt.

## 4. Automatic Calculation Mode for Multiple UDRM Values
The program can calculate transient processes for multiple UDRM values automatically, without requiring manual `Ctrl + C` presses or UDRM value changes in the "MTUT" file.

1. Open the configuration file in:  
   `treada-launcher\wrapper\config\config.json`
2. Set the following flags:  
   `"udrm_vector_mode": true`  
   `"auto_ending": true`
3. Create or open a file in:  
   `treada-launcher\data\input\UDRM.txt`
4. Enter the required UDRM values, each on a new line. Decimal separators can be either dots or commas.

## 5. Additional Features
The program offers several additional modes via command-line arguments.  
Example: `py .\treada_launcher.py --collect-distr --gui`

### Available Arguments and Modes:
- `--plot-res, -r`  
  Generate plots of transient process results.
- `--collect-distr, -d (--gui)`  
  Generate distribution diagrams from temporal `WW` files produced during program execution.  
  **Requirements:**  
  a) Set `"preserve_distributions": true` in the configuration file:  
     `treada-launcher\wrapper\config\config.json`.  
  b) After launching with `--collect-distr`, enter the `--extract` argument in the terminal dialog and follow instructions.  
  **Graphical Mode:**  
  a) Select root folders corresponding to the program's steps in the file manager.  
  b) Click "Extract" and wait for the process to complete.  
  c) Choose the desired distribution from the dropdown menu.  
  d) Specify the indices for intermediate result distributions (numeric values).
- `--plot-fields-integral, -f`  
  Calculate and plot the integral of the electric field for the last point of step 1 and the last point of step 2.

---

The utility is based on the "Treada" program developed by Yaroslav Borisovich Martynov.  
Learn more about the project and its authors here:  
[https://github.com/OutlyingWest/treada-launcher.git](https://github.com/OutlyingWest/treada-launcher.git)
