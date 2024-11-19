import pandas as pd
df = pd.read_csv("cities.csv")


def df_to_xml(df):
    xml_rows = []
    for _, row in df.iterrows():
        state_data = (
            f'    <state>\n'
            f'        <state_id>{row["state_id"]}</state_id>\n'
            f'        <state_code>{row["state_code"]}</state_code>\n'
            f'        <state_name>{row["state_name"]}</state_name>\n'
            f'    </state>'
        )

        country_data = (
            f'    <country>\n'
            f'        <country_id>{row["country_id"]}</country_id>\n'
            f'        <country_code>{row["country_code"]}</country_code>\n'
            f'        <country_name>{row["country_name"]}</country_name>\n'
            f'    </country>'
        )

        xml_rows.append(f'<row>\n'
                        f'    <id>{row["id"]}</id>\n'
                        f'    <name>{row["name"]}</name>\n'
                        f'{state_data}\n'
                        f'{country_data}\n'
                        f'    <latitude>{row["latitude"]}</latitude>\n'
                        f'    <longitude>{row["longitude"]}</longitude>\n'
                        f'    <wikiDataId>{row["wikiDataId"]}</wikiDataId>\n'
                        f'</row>')

    return '<data>\n' + '\n'.join(xml_rows) + '\n</data>'

xml_output = df_to_xml(df)

with open("cities.xml", 'w',encoding='utf-8' ) as file:
    file.write(xml_output)