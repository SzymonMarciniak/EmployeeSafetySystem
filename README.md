# Documentation:
https://github.com/SzymonMarciniak/EmployeeSafetySystem/blob/main/Documentation.pdf

# RUN 

# 1. Create virtual environment 
    conda create -n 'name' python=3.9.7

# 2. Install dependencties 
    pip install -r requirements.txt

    If you use windows 10/11 you must also install: 
        pywin32==304

# 3. Start MySQL 
## For linux:


#### Install mysql-server:
        sudo apt install mysql-server

#### Start mysql:
        sudo service mysql start

#### Configure your mysql:
        sudo mysql_secure_installation

#### Open mysql:
        sudo mysql -u root

#### Create database "employee_safety_system":
        CREATE TABLE employee_safety_system;

#### Grant privileges to root:
        DROP USER 'root'@'localhost';

        CREATE USER 'root'@'%' IDENTIFIED BY 'password123';

        GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

        FLUSH PRIVILEGES;
##### If you have different password, please change line 40 in database.py file


# 4. Run application 
    python3 main.py
