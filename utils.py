from cryptography.fernet import Fernet
import base64, sqlite3, random, string, requests, time, sys, os

class Cipher:
    def __init__(self, db_path, verbose=False):
        self.verbose = verbose
        self.SQLite = SQLite(db_path, verbose)
        self.cur = self.SQLite.cur
        if self.SQLite.checkTable("cipher") is False:
            self.SQLite.makeCipherTable(self.makeKey())
            self.key = self.getKey()
            if verbose is True: print("Cipher Initialized With Key: ", self.key)
        else:
            self.key = self.getKey()
            if verbose is True: print("Cipher Initialized With Key: ", self.key)

    def makeKey(self):
        cipher_key = Fernet.generate_key()
        encoded_key = base64.b64encode(cipher_key)
        if self.verbose is True:
            print("Generating Key. . .")
            print("Key: ", cipher_key)
            print("Encoded Key: ", encoded_key) 
        return encoded_key

    def getKey(self):
        self.cur.execute("SELECT key FROM cipher")
        encoded_key = self.cur.fetchone()[0]
        cipher_key = base64.b64decode(encoded_key)
        if self.verbose is True:
            print("Retrieving Key. . .")
            print("Encoded Key: ", encoded_key)
            print("Key: ", cipher_key)
        return cipher_key.decode()
    
    def generatePassword(self, length=16):
        if self.verbose is True: print("Generating password with length {}.".format(length))
        low_chars = "abcdefghijklmnopqrstuvwxyz"
        alpha_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        num_chars = "0123456789"
        special_chars = "!@#$%^&*()_+-=[]{};:,./<>?"
        for l in range(length):
            password = random.choice(low_chars) + random.choice(alpha_chars) + random.choice(num_chars) + random.choice(special_chars)
            password += ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length - 4))
        if self.verbose is True: print("Generated password: ", password)
        return password

    def encrypt(self, plain_text):
        cipher_suite = Fernet(self.key)
        cipher_text = cipher_suite.encrypt(plain_text.encode())
        encoded_text = base64.b64encode(cipher_text)
        if self.verbose is True:
            print("Encrypting Data. . .")
            print("Data: ", plain_text)
            print("Cipher Text: ", cipher_text)
            print("Encoded Text: ", encoded_text)
        return encoded_text
    
    def decrypt(self, encoded_text):
        cipher_suite = Fernet(self.key)
        decoded_data = base64.b64decode(encoded_text)
        plain_text = cipher_suite.decrypt(decoded_data)
        if self.verbose is True:
            print("Decrypting Data. . .")
            print("Encoded Data: ", encoded_text)
            print("Decoded Data: ", decoded_data)
            print("Plain Text: ", plain_text)
        return plain_text.decode()
    
    def checkLogin(self, username, password):
        if self.verbose is True: print("Checking login for user {} with password {}.".format(username, password))
        self.cur.execute("SELECT username, password FROM users")
        for row in self.cur.fetchall():
            if self.decrypt(row[0]) == username and self.decrypt(row[1]) == password:
                if self.verbose is True: print("Login successful.")
                return True
            else:
                if self.verbose is True: print("Login failed.")
                return False
    def queryCells(self, query):
        if self.verbose is True: print("Querying cells for {}.".format(query))
        cells = self.SQLite.countCellTables()
        results = []  # Create a list to store the results
        for cell in cells:
            platform, username, password, email, website = self.SQLite.readCell(cell)
            platform = self.decrypt(platform)
            username = self.decrypt(username)
            password = self.decrypt(password)
            email = self.decrypt(email)
            website = self.decrypt(website)
            if query in platform or query in username or query in password or query in email or query in website:
                if self.verbose is True: print("Found {} in cell{}.".format(query, cell))
                results.append((cell, platform, username, password, email, website))  # Append the found result to the list
            else:
                if self.verbose is True: print("Did not find {} in cell{}.".format(query, cell))
                continue
        return results  # Return the list of found results
    
class SQLite:
    def __init__(self, db_path, verbose=False):
        self.verbose = verbose
        self.conn = sqlite3.connect(db_path, verbose)
        if verbose is True: print("Connected to database at {}.".format(db_path))
        self.cur = self.conn.cursor()

    def makeCipherTable(self, key):
        self.cur.execute("CREATE TABLE IF NOT EXISTS cipher (key TEXT)")
        self.cur.execute("INSERT INTO cipher VALUES (?)", (key,))
        self.conn.commit()
        if self.verbose is True:
            print("Creating Cipher Table. . .")
            print("Inserted Key: ", key)

    def checkTable(self, table_name):
        if self.verbose is True: print("Checking for table {}. . .".format(table_name))
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if self.cur.fetchone() is None:
            if self.verbose is True: print("Table does not exist.")
            return False
        else:
            if self.verbose is True: print("Table exists.")
            return True
        
    def registerUser(self, username, password):
        self.cur.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
        self.cur.execute("INSERT INTO users VALUES (?, ?)", (username, password))
        self.conn.commit()
        if self.verbose is True:
            print("Registering user {} with password {}.".format(username, password))
    

    def editUser(self, username, password):
        self.cur.execute("UPDATE users SET username=?, password=?", (username, password))
        self.conn.commit()
        if self.verbose is True:
            print("Editing user {} with password {}.".format(username, password))

    def countCellTables(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'cell%'")
        tables = self.cur.fetchall()
        if self.verbose is True:
            print("Counting cell tables. . .")
            print("Number of cell tables: ", len(tables))
        return [int(table[0][4:]) for table in tables]

    def addPassword(self, platform, username, password, email, website):
        cell = len(self.countCellTables()) + 1
        while self.checkTable("cell{}".format(cell)):
            if self.verbose:
                print("Cell{} already exists. Trying next cell.".format(cell))
            cell += 1
        if self.verbose:
            print("Adding password to cell{} for platform {} with username {} and password {}.".format(cell, platform, username, password))
        self.cur.execute("CREATE TABLE IF NOT EXISTS cell{} (platform TEXT, username TEXT, password TEXT, email TEXT, website TEXT)".format(cell))
        self.cur.execute("INSERT INTO cell{} VALUES (?, ?, ?, ?, ?)".format(cell), (platform, username, password, email, website))
        self.conn.commit()
        if self.verbose:
            print("Password saved successfully to cell{}.".format(cell))
    
    def editPassword(self, cell, platform, username, password, email, website):
        if self.verbose is True: print("Editing password for platform {} with username {} and password {}.".format(platform, username, password))
        self.cur.execute("UPDATE cell{} SET platform=?, username=?, password=?, email=?, website=?".format(cell), (platform, username, password, email, website))
        self.conn.commit()
        if self.verbose is True: print("Password saved successfully to cell{}.".format(cell))

    def readCell(self, cell_num):
        self.cur.execute(f"SELECT platform, username, password, email, website FROM cell{cell_num}")
        platform, username, password, email, website = self.cur.fetchone()
        if self.verbose is True:
            print("Reading cell{}. . .".format(cell_num))
            print("Cell{} data: ".format(cell_num), (platform, username, password, email, website))
        return platform, username, password, email, website
    
    def getUsername(self):
        self.cur.execute("SELECT username FROM users")
        username = self.cur.fetchone()[0]
        if self.verbose is True:
            print("Retrieving username. . .")
            print("Username: ", username)
        return username
    
class Update:
    def __init__(self, verbose=False):
        self.verbose = verbose
        if self.verbose is True: print("Initializing update. . .")
        self.rep_owner = "aiden04"
        self.rep_name = "PsychoPass"
        self.rep_url = f"https://api.github.com/repos/{self.rep_owner}/{self.rep_name}"
        self.raw_rep_url = f"https://raw.githubusercontent.com/{self.rep_owner}/{self.rep_name}"
        if self.verbose is True:
            print("Owner: ", self.rep_owner)
            print("Repository Name: ", self.rep_name)
            print("Repository URL: ", self.rep_url)
    def checkForUpdate(self):
        if self.verbose is True: print("Checking for update. . .")
        if self.verbose is True: print("Requests URL: ", f"{self.rep_url}/releases/latest")
        response = requests.get(f"{self.rep_url}/releases/latest")
        if response:
            release = response.json()
            latest_version = release["tag_name"]
            if self.verbose is True: print("Latest Version: ", latest_version)
            if latest_version > "1.2.0":
                if self.verbose is True: print("Update available.")
                return True
            else:
                if self.verbose is True: print("No update available.")
                return False
        else:
            if self.verbose is True: print("Update information not available.")
            return False
    def update(self):
        if self.verbose is True: print("Updating. . .")
        time.sleep(1)
        progress = 0
        while progress < 100:
            out_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "update"))
            yield progress + 20
            if self.verbose is True: print("Output Path: ", out_path)
            main_url = f"{self.raw_rep_url}/nightly/main.py"
            psychopass_url = f"{self.raw_rep_url}/nightly/psychopass.py"
            utils_url = f"{self.raw_rep_url}/nightly/utils.py"
            ico_url = f"{self.raw_rep_url}/nightly/assets/icon.ico"
            logo_url = f"{self.raw_rep_url}/nightly/assets/logo.png"
            progress += 20
            yield progress
            time.sleep(1)
            if self.verbose is True: print("Urls: ", main_url, psychopass_url, utils_url)
            r_main = requests.get(main_url)
            r_psychopass = requests.get(psychopass_url)
            r_utils = requests.get(utils_url)
            r_ico = requests.get(ico_url)
            r_logo = requests.get(logo_url)
            progress += 20
            yield progress 
            time.sleep(1)
            content = [["main.py", r_main], ["psychopass.py", r_psychopass], ["utils.py", r_utils], ["assets/icon.ico", r_ico], ["assets/logo.png", r_logo]]
            if r_main and r_psychopass and r_utils:
                if self.verbose is True: print("Successfully requested files.")
                if not os.path.exists(out_path):
                    os.makedirs(out_path)
                    os.makedirs(f"{out_path}/assets")
                progress += 20
                yield progress
                time.sleep(1)
                for file in content:
                    if self.verbose is True: print("Writing file {} to {}.".format(file[0], out_path))
                    with open(os.path.abspath(os.path.join(out_path, file[0])), "wb") as f:
                        if self.verbose is True: print("File content: ", file[1].content)
                        f.write(file[1].content)
                        time.sleep(1)
                        if self.verbose is True: print("Successfully wrote file {} to {}.".format(file[0], out_path))
                        progress += 10 
                        yield progress
            else:
                if self.verbose is True: print("Failed to request files.")
                return
