import boto3

dynamodb = boto3.resource('dynamodb', region_name='us-west-2', endpoint_url='http://localhost:8000')

table = dynamodb.create_table(
    TableName='FridgeGenie',
    KeySchema=[
        {
            'AttributeName': 'item',
            'KeyType': 'HASH'  #Partition key
        },
        {
            'AttributeName': 'expiration_date',
            'KeyType': 'RANGE'  #Sort key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'expiration_date',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'item',
            'AttributeType': 'S'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)

print("Table status:", table.table_status)