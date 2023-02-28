from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['PUT'])
def RepeatGetInfoView(request):
    latitude = request.data['latitude']
    longitude = request.data['longitude']
    speed = request.data['speed']
    print(latitude)
    print(longitude)
    print(speed)
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
