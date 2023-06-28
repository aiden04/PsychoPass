
![logo-no-background](https://github.com/aiden04/PsychoPass/assets/9298623/c8139a9e-9eba-4d9a-b9ab-133785936861)

The PsychoPass program is a password management tool designed to securely store and manage user passwords. It provides a user-friendly graphical user interface (GUI) for interacting with the program.

## Features

- **Login**: Users can log in to access their password vault.
- **Save Passwords**: Users can save their passwords along with associated information such as username, email, and website.
- **Generate Passwords**: Users can generate strong and secure passwords.
- **Options**: Users can access various program options, such as resetting their login information.
- **Clear Passwords**: Users can clear all saved passwords from the vault.
- **Encryption**: Passwords are encrypted using a secure encryption algorithm.
- **File Storage**: Passwords are stored in a file for persistent storage.

## Dependencies

The PsychoPass program relies on the following dependencies:

- Python 3.6 or above
- PySimpleGUI library
- Cryptography library

## Media
### Login
![image](https://github.com/aiden04/PsychoPass/assets/9298623/3149863b-80a9-47fc-b31a-6b6da0b1c9bd)
### Login Creation
![image](https://github.com/aiden04/PsychoPass/assets/9298623/4ac5cb2b-2f18-4eee-98e6-ccab189b2298)
### Main Menu
![image](https://github.com/aiden04/PsychoPass/assets/9298623/5aabc121-b5d5-4f5b-9bd7-a88541df2e20)
### Password Saver
![image](https://github.com/aiden04/PsychoPass/assets/9298623/7c690559-f5ce-4751-bb84-a8490701bae9)
### Password Generator
![image](https://github.com/aiden04/PsychoPass/assets/9298623/54e0824e-e1c6-447e-8ae0-657c14a32547)
### Options
![image](https://github.com/aiden04/PsychoPass/assets/9298623/d82f02b6-3677-414f-8a21-7be96fc9f22c)

## Build
If you want to build this into an executable from the source code, follow instructions below:
Open a new windows terminal where you want then enter these commands.
```
git clone https://github.com/aiden04/PsychoPass.git
cd PsychoPass
pip install -r requirements.txt
pyinstaller --onefile --icon icon.ico fileImport.pyw
pyinstaller --icon icon.ico Main.pyw
```
Once you've done the steps above, copy `icon.ico`, `logo.png`, and open the new `Dist` folder inside the root. You can paste the files in the `Dist` folder, then just move all files into the `Main` directory. And thats it, you've compiled PsychoPass.
If you would want to go further and compile the installer for on click file support for `.pyp`, that you will need to download the [Inno Installer](https://jrsoftware.org/isdl.php). After you've installed inno, you can just right click the `PsychoPassInstaller.iss` and click compile. After that a the file will compile and create an installer.
## Usage

To run the PsychoPass program, follow these steps:
- Download `PsychoPassInstaller.exe` from releases and install PsychoPass.
- Once installed, launch the shortcut on the desktop and your all ready!

Please note that the program may require additional setup or configuration depending on your specific environment or use case.

## License

The PsychoPass program is released under the MIT License. You can find the detailed license information in the `LICENSE` file included with the program files.

## Contributions

Contributions to the PsychoPass program are welcome! If you find any issues or have suggestions for improvements, please submit them via the project's GitHub repository.
