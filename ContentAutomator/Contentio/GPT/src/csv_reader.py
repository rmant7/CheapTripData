import polars as pl


class CSVReader:  
    def __init__(self, path: str) -> None:
        self.df_cities_countries = pl.read_csv(path)
        self.numrows = self.df_cities_countries.shape[0]
    
    
    def get_cities_countries(self, from_: int=0, to_: int=-1) -> list:
        """
        Returns sorted list of the cities and countries. Parameters:'from_' and 'to_' define a list slice.
        """
        cities_countries = self.df_cities_countries[['city', 'country']].sort('city')
        return cities_countries[from_:to_].rows()
        
    
    def get_cities(self, from_: int=0, to_: int=-1) -> list:
        cities = sorted(self.df_cities_countries['city'])
        return cities[from_:to_]
    
    
    def get_city_name(self, id: int) -> str:
        """Takes an integer id as input and returns the corresponding city name from the dataframe 'df_cities_countries'. It filters the dataframe based on the id and returns the first value of the 'city' column.

        Args:
            id (int): city id

        Returns:
            str: city name
        """
        return self.df_cities_countries.filter(pl.col('id_city') == id)['city'][0]
    
    
    def get_city_id(self, name: str) -> int:
        """This function takes in a city name as a string and returns the corresponding city ID as an integer. It does this by filtering the dataframe of cities and countries for the row where the 'city' column matches the input name, and then returning the value in the 'id_city' column for that row. 

        Args:
            name (str): city name

        Returns:
            int: city id
        """
        return self.df_cities_countries.filter(pl.col('city') == name)['id_city'][0]
    
    
    def get_numrows(self):
        return self.numrows
    
