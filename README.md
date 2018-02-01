# MyMeal
Web Application for managing food inventory, favorite meals, and meal suggestions.

# Setup 
* Follow setup steps mentioned in https://docs.djangoproject.com/en/2.0/howto/windows/
	- cURl - https://curl.haxx.se/download.html
		-use DOWNLOAD WIZARD to get the correct one for your machine 
		- extract/unzip to a place you won't delete it
		- add that directory as a environment variable
* Download SQLite sqlite-tools-win32-x86-3220000.zip (1.62 MiB)	(OR other operating system equivalent) from https://www.sqlite.org/download.html
		- extract/unzip to a place you won't delete it
		- add that directory as a environment variable
* Clone this mealapp project to a working directory

# Running the Application
* Navigate to your mealapp directory e.g. C:/MyDirectory/.../mealapp
* Open terminal/command prompt and run
	* .\manange.py runserver
	* This will automatically launch the application at 127.0.0.1:8000
	* Any working changes you make to files in the mealapp project will be watched and recompiled while the server is running 
	* Refresh the webpage to see changes/errors

# Updating the Database
When your datatables are out of sync with the models in the project, run the following commands:

python manage.py makemigrations
python manage.py migrate

# Checking the Database
If you want to run test queries or see what a datatable looks like in the database, run the following in the terminal/command prompt:

sqlite3 db.sqlite3

To see the list of tables created use:

.tables

Example of selecting fields from a table:

SELECT name, date FROM groceryList_grocerylist;

