
# TrackMyVaccine

## To install all required libraries: 
`pip install -r requirements.txt`


  

## To run the application: 
<ul>
	<li>git pull origin master</li>
	<li> Edit Database</li>
	<ul>
		<li>open file explorer and go to c->program files->mysql->mysqlserver->bin</li>
		<li>paste the database file in that directory</li>
		<li>open cmd prompt in that directory</li>
		<ul>
			<li> `mysql -u root` </li>
			<ul>
				<li> `drop database trackmyvaccine` </li>
				<li> `create database trackmyvaccine` </li>
				<li> `exit` </li>
			</ul>
			<li> `mysql -u root trackmyvaccine < filename.sql` </li>
		</ul>
	</ul>
	<li>open terminal in directory of the code</li>
    <li> `python manage.py runserver` </li>
</ul>

