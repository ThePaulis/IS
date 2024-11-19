<rows>{
  for $city in doc("cities.xml")//row
  where $city/country/country_code = "BR"
  return $city
}</rows>