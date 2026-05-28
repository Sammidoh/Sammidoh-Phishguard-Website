import csv
import json
from io import StringIO
from flask import Response

def export_to_csv(data, filename='export.csv'):
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(data[0].keys())
    for row in data:
        cw.writerow(row.values())
    output = si.getvalue()
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': f'attachment; filename={filename}'})

def export_to_json(data, filename='export.json'):
    return Response(json.dumps(data, default=str), mimetype='application/json', headers={'Content-Disposition': f'attachment; filename={filename}'})