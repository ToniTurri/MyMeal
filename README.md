<p align="center"> <img src="/static/img/MyMealFinal_Orange.png" /> </p>

# MyMeal
Web Application for managing food inventory, recipes, grocery lists and meal suggestions.

Developed by:
- Toni Turri (@ToniTurri)
- Paul Pieper (@ppieper)
- Brendan Shanahan (@brendanshanahan)
- Finn Coughlin (@finn17)

# Image Gallery

<p align="center">
	<img src="/static/img/register.PNG" height="350px" style="display:block; float:left;"/>
	<img src="/static/img/inventory.PNG" height="350px" style="display:block; float:left;"/>
	<img src="/static/img/grocery_list.PNG" height="350px" style="display:block; float:left;"/>
</p>
<p align="center">
	<img src="/static/img/recipes.PNG" height="350px" style="display:block; float:left;"/>
</p>
<p align="center">
	<img src="/static/img/recipe_finder.PNG" height="300px" style="display:block; float:left;"/>
	<img src="/static/img/recipe_detail.PNG" height="300px" style="display:block; float:left;"/>
</p>

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

# Packages
* View requirements.txt in the main directory of this project and ensure you have all the packages installed

# Running the Application
* Navigate to your mealapp directory e.g. C:/MyDirectory/.../MyMeal
* Open terminal/command prompt and run
	* .\manange.py runserver
	* This will automatically launch the application at 127.0.0.1:8000
	* Any working changes you make to files in the mealapp project will be watched and recompiled while the server is running 
	* Refresh the webpage to see changes/errors
* RecipeFinder:
	* For the recipe finder to work, you will need a Yummly API key and ID and [update these variables](https://github.com/ToniTurri/MyMeal/blob/master/recipeFinder/views.py#L21) with their appropriate values.

# Creating the Database
To initially create the database, run the following command:

python manage.py migrate	
	
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

