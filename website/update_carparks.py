import urllib.request
import json

# Format the carpark information to match the database
def format_carpark_information(record):
    fattributes = list()
    fattributes.append(record.get("address"))
    fattributes.append(float(record.get("x_coord")))
    fattributes.append(float(record.get("y_coord")))
    fattributes.append(record.get("car_park_type"))
    fattributes.append(record.get("type_of_parking_system"))
    fattributes.append(record.get("short_term_parking"))
    fattributes.append(record.get("free_parking"))

    np = record.get("night_parking")
    if np == "YES":
        fattributes.append(True)
    elif np == "NO":
        fattributes.append(False)
    else:
        print("Error")
        return None

    fattributes.append(int(record.get("car_park_decks")))
    fattributes.append(float(record.get("gantry_height")))

    cpb = record.get("car_park_basement")
    if cpb == "Y":
        fattributes.append(True)
    elif cpb == "N":
        fattributes.append(False)
    else:
        print("Error")
        return None
    
    return fattributes

# HDB carpark information mainly consists of information that changes rarely
# We will only need to update everytime the webapp is started
def update_carparks():
    print("XXXXX Updating carparks XXXXX")
    from . import db
    from .models import CarPark

    url = 'https://data.gov.sg/api/action/datastore_search?resource_id=139a3035-e624-4f56-b63f-89ae28d4ae4c'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    req = urllib.request.Request(url, headers=headers)
    fileobj = urllib.request.urlopen(req)
    json_data = json.load(fileobj)

    records = json_data['result']['records']

    for record in records:
        fattributes = format_carpark_information(record)
        carpark = CarPark.query.get(record.get("car_park_no"))

        if carpark:
            carpark.address = fattributes[0]
            carpark.x_coord = fattributes[1]
            carpark.y_coord = fattributes[2]
            carpark.car_park_type  = fattributes[3]
            carpark.type_of_parking_system = fattributes[4]
            carpark.short_term_parking = fattributes[5]
            carpark.free_parking = fattributes[6]
            carpark.night_parking = fattributes[7]
            carpark.car_park_decks = fattributes[8]
            carpark.gantry_height = fattributes[9]
            carpark.car_park_basement = fattributes[10]
        else:
            carpark = CarPark(
                car_park_no = record.get("car_park_no"),
                address = fattributes[0],
                x_coord = fattributes[1],
                y_coord = fattributes[2],
                car_park_type  = fattributes[3],
                type_of_parking_system = fattributes[4],
                short_term_parking = fattributes[5],
                free_parking = fattributes[6],
                night_parking = fattributes[7],
                car_park_decks = fattributes[8],
                gantry_height = fattributes[9],
                car_park_basement = fattributes[10],
                # attributes below are not in the dataset being queried
                total_lots = None,
                lots_available = None,
                lot_type = None,
                lot_info_last_updated = None
            )
            db.session.add(carpark)
    
    db.session.commit()

def update_carparks_availability():
    print("XXXXX Updating carparks availability XXXXX")
    from . import db
    from .models import CarPark

    url = 'https://api.data.gov.sg/v1/transport/carpark-availability'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    req = urllib.request.Request(url, headers=headers)
    fileobj = urllib.request.urlopen(req)
    json_data = json.load(fileobj)

    records = json_data['items'][0]['carpark_data']

    for record in records:
        carpark_info = record.get("carpark_info")[0]

        total_lots = int(carpark_info.get("total_lots"))
        lots_available = int(carpark_info.get("lots_available"))
        lot_type = carpark_info.get("lot_type")
        lot_info_last_updated = record.get("update_datetime")

        carpark = CarPark.query.get(record.get("carpark_number"))

        # update availability if the carpark exists in the database
        # otherwise, omit
        if carpark:
            carpark.total_lots = total_lots
            carpark.lots_available = lots_available
            carpark.lot_type = lot_type
            carpark.lot_info_last_updated = lot_info_last_updated

    db.session.commit()