import pandas as pd
import json

def xlsx_to_json(xlsx_path, json_path):
    # excel okuma
    df = pd.read_excel(xlsx_path)
    # boşlukları temizleme
    df.columns = df.columns.str.replace(" ", "")

    # dataframe json kaydetme
    records = df.to_dict(orient='records')

    if records is not None:
        i = 1
        # Her kaydı düzenleme
        for record in records:
            new_record = {}
            # Ayırma ve dictionary'e ekleme
            for col in df.columns:
                keys = col.split(',')
                values = str(record[col]).split(',') if col in record else [""]
                new_record.update(zip(keys, values))
            if 'CaseID' in new_record:
                new_record['CaseID'] = int(new_record['CaseID'])
            new_record = {k[0].lower() + k[1:]: v for k, v in new_record.items()}
            new_record["processId"] = 1
            new_record["id"] = i
            i += 1
            record.clear()
            record.update(new_record)

    with open(json_path, 'w') as json_file:
        json_file.write(json.dumps(records, indent=2))

# ornek kullanım
xlsx_file_path = "/Users/oguzcanakyol/Desktop/amatisBackend/mock/PurchasingExample.xlsx"
json_file_path = "/Users/oguzcanakyol/Desktop/amatisBackend/mock/mockData.json"
xlsx_to_json(xlsx_file_path, json_file_path)



def xlsx_to_dataframe(xlsx_path):
    # excel okuma
    df = pd.read_excel(xlsx_path)
    # boşlukları temizleme
    df.columns = df.columns.str.replace(" ", "")

    # dataframe json kaydetme
    records = df.to_dict(orient='records')

    if records is not None:
        i = 1
        # Her kaydı düzenleme
        for record in records:
            new_record = {}
            # Ayırma ve dictionary'e ekleme
            for col in df.columns:
                keys = col.split(',')
                values = str(record[col]).split(',') if col in record else [""]
                new_record.update(zip(keys, values))
            if 'CaseID' in new_record:
                new_record['CaseID'] = int(new_record['CaseID'])
            record.clear()
            record.update(new_record)

    result_df = pd.DataFrame(records)

    return result_df

# örnek kullanım
xlsx_file_path = "/Users/oguzcanakyol/Desktop/amatisBackend/mock/PurchasingExample.xlsx"
result_dataframe = xlsx_to_dataframe(xlsx_file_path)

print(result_dataframe)

