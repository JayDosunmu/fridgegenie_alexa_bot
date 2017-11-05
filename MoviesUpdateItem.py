from __future__ import print_function # Python 2/3 compatibility
import boto3
import json
import decimal

# Helper class to convert a DynamoDB item to JSON.
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url="http://localhost:8000")

table = dynamodb.Table('Movies')

title = "Little Black Book"
year = 2004

response = table.update_item(
    Key={
        'title': title,
        'year': year
    },
    UpdateExpression="set info.rating = :r, info.plot = :p, info.actors = :a",
    ExpressionAttributeValues={
        ':r': decimal.Decimal(5.5),
        ':p': 'Watch it for the plot',
        ':a': ['aaron', 'jamal', 'nasart'],
    },
    ReturnValues="UPDATED_NEW"
)

print("Update item succeeded:")
print(json.dumps(response, indent=4, cls=DecimalEncoder))