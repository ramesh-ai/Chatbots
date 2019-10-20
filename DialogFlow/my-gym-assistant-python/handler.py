import os
from flask import Flask, request, jsonify
app = Flask(__name__)

PORT = os.environ.get('PORT') or 5000

@app.route('/', methods=['POST'])
def webhook():
    response = {}
    exercises = ['pushups', 'pullups', 'chinups', 'legpress']
    queryResult = request.get_json()['queryResult']
    fulfillmentText = queryResult['fulfillmentText']
    nextExercise = exercise = 'pushups'

    if 'exercise' in queryResult['parameters']:
        exercise = queryResult['parameters']['exercise']

    if 'nextExercise' in queryResult['parameters']:
        exercise = queryResult['parameters']['nextExercise']    

    if exercise in exercises:
        found = exercises.index(exercise)
        if found is not None and (exercise != 'legpress'):
            nextExercise = exercises[found + 1] 
        else:
            response['fulfillmentText'] = 'That\'s enough for today, take some rest'
            return jsonify(response) 


    if 'outputContexts' in queryResult:
        outputContext = queryResult['outputContexts'][0]
        response['outputContexts'] = []
        params = {}
        params['name'] = outputContext['name']  
        params['lifespanCount'] = outputContext['lifespanCount']
        params['parameters'] = {}
        params['parameters']['exercise'] = nextExercise
        params['parameters']['nextExercise'] = nextExercise
        response['outputContexts'].append(params)

    response['fulfillmentText'] = fulfillmentText.replace('_exercise', nextExercise)

    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True, port=PORT, host='0.0.0.0')    