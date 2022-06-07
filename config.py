import os

headers = {'x-rapidapi-host': "hotels4.p.rapidapi.com", 'x-rapidapi-key': f"{os.getenv('RAPIDAPI_KEY')}"}
url = "https://hotels4.p.rapidapi.com/locations/v2/search"
url_2 = "https://hotels4.p.rapidapi.com/properties/list"
url_3 = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"


cities = ['London', 'Paris', 'Amsterdam', 'New York', 'Pekin', 'Praga', 'Berlin', 'Brussels', 'Bucharest'
          'Budapest', 'Dublin', 'Florence', 'Geneva', 'Havana', 'Helsinki', 'Lagos', 'Madrid', 'Manchester',
          'Melbourne', 'Monaco', 'Monte Carlo', 'Montreal', 'New Orleans', 'Orlando', 'Orleans', 'Oslo', 'Ottawa',
          'Rio-de-Janeiro', 'Rome', 'San Francisco', 'Seoul', 'Sicily', 'Sydney', 'Venice', 'Vienna', 'Vilnuis',
          'Zurich', 'Milan', 'Dallas', 'Kansas City', 'New Orleans', 'Philadelphia', 'Minsk', 'Washington',
          'Chicago', 'Detroit'
          ]

path = os.path.abspath(os.path.join('..', '..', 'Desktop', 'history_db.db'))
