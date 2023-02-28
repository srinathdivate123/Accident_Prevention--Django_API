from rest_framework.decorators import api_view
from rest_framework.response import Response
import json
@api_view(['GET', 'POST'])
def RepeatGetInfoView(request):
    if request.method == 'GET':
        return Response({"Status": "This is test data sent by GET request"})
    if request.method == 'POST':
        content = request.data['_content']
        content.replace('\r\n', '')
        content = json.loads(content)
        latitude = content['latitude']
        longitude = content['longitude']
        speed = content['speed']
        date = content['date']
        time = content['time']
        gender = content['gender']
        age = content['age']
        return Response({"success":True})

@api_view(['GET'])
def testGetView(request):
    ans = [
        {
            'firstKey': 'val1',
            'secondKey': 'val2',
            'thirdKey': None,
            'fourthKey': True,
        },
        {
            '2firstKey': 'val1',
            '2secondKey': 'val2',
            '2thirdKey': None,
            '2fourthKey': True,
        },
        {
            '3firstKey': 'val1',
            '3secondKey': 'val2',
            '3thirdKey': None,
            '3fourthKey': True,
        },
    ]
    return Response(ans)
