


import matplotlib.pyplot as plt
from io import BytesIO
import base64
import matplotlib.pyplot as plt
import networkx as nx
import pm4py
import pandas as pd
import graphviz
import base64
import json
import d3blocks
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
import json
import pydotplus

def capture_heuristics_net_image(heu_net):
    image = pm4py.view_heuristics_net(heu_net)

    buffer = BytesIO()
    image.savefig(buffer, format="png", bbox_inches='tight')
    plt.close(image)

    image_bytes = buffer.getvalue()

    encoded_image = base64.b64encode(image_bytes).decode("utf-8")

    return encoded_image
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
def generate_heuristics_net_image():
    try:
        dataframe = xlsx_to_dataframe("/Users/oguzcanakyol/Desktop/amatisBackend/mock/PurchasingExample.xlsx")
        dataframe = pm4py.format_dataframe(dataframe, case_id='CaseID', activity_key='Activity',
                                           start_timestamp_key='StartTimestamp', timestamp_key='CompleteTimestamp')
        log = pm4py.convert_to_event_log(dataframe)
        heu_net = pm4py.discover_heuristics_net(log)
        
        if heu_net is None:
            raise ValueError("Heuristics Net is not generated successfully.")
        

        dot_graph = pm4py.visualization.heuristics_net.visualizer.get_graph(heu_net=heu_net)
        dot_format = dot_graph.to_string()
       

        pydot_graph = pydotplus.graph_from_dot_data(dot_format)
        nodes = []
        edges = []
        for edge in pydot_graph.get_edges():
            source = edge.get_source().strip('"')
            target = edge.get_destination().strip('"') 
            weight = edge.get_attributes().get('weight', 1.0)  
            edges.append({"source": source, "target": target, "weight": float(weight)})
            
            if {"id": source, "label": source} not in nodes:
                nodes.append({"id": source, "label": source})
            if {"id": target, "label": target} not in nodes:
                nodes.append({"id": target, "label": target})
            

        d3_data = {
            "nodes": nodes,
            "links": edges
        }

        json_data = json.dumps(d3_data, indent=2)

        with open("/Users/oguzcanakyol/Desktop/amatisBackend/image/d3_data.json", 'w') as json_file:
            json_file.write(json_data)

        return json_data
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    
generate_heuristics_net_image()
