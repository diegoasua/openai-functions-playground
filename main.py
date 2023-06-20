import openai
import json
import os
import requests
import math

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']


def get_current_weather(**kwargs):
  location = kwargs.get('location', '')
  unit = kwargs.get('unit', 'fahrenheit')
  weather_info = {
    "location": location,
    "temperature": "72",
    "unit": unit,
    "forecast": ["sunny", "windy"],
  }
  return json.dumps(weather_info)


def say_my_name(**kwargs):
  return json.dumps({"info": "Heissenberg"})


def get_exchange_rate(**kwargs):
  response = requests.get('https://api.exchangerate-api.com/v4/latest/USD')
  data = response.json()
  return json.dumps(data)

def calculate_hypotenuse(**kwargs):
  a = float(kwargs.get('a', 0))
  b = float(kwargs.get('b', 0))
  hypotenuse = math.sqrt(a**2 + b**2)
  return json.dumps({"hypotenuse": hypotenuse})

available_functions = {
  "get_current_weather": get_current_weather,
  "say_my_name": say_my_name,
  "get_exchange_rate": get_exchange_rate,
  "calculate_hypotenuse": calculate_hypotenuse,
}

def run_conversation():
  messages = [{"role": "user", "content": "My triangle with 90 degree angle has catetes 4.89 and 95.345 cm. What's the hypotenuse?"}]
  functions = [{
    "name": "get_current_weather",
    "description": "Get the current weather in a given location",
    "parameters": {
      "type": "object",
      "properties": {
        "location": {
          "type": "string",
          "description": "The city and state, e.g. San Francisco, CA",
        },
        "unit": {
          "type": "string",
          "enum": ["celsius", "fahrenheit"]
        },
      },
      "required": ["location"],
    },
  }, {
    "name": "say_my_name",
    "description": "Returns a fixed value",
    "parameters": {
      "type": "object",
      "properties": {},
    },
  }, {
    "name": "get_exchange_rate",
    "description": "Get the latest USD exchange rate from an external API",
    "parameters": {
      "type": "object",
      "properties": {},
    },
  }]
  functions.append({
  "name": "calculate_hypotenuse",
  "description": "Calculates the hypotenuse of a right triangle using the Pythagorean theorem",
  "parameters": {
    "type": "object",
    "properties": {
      "a": {
        "type": "number",
        "description": "Length of the first leg of the right triangle",
      },
      "b": {
        "type": "number",
        "description": "Length of the second leg of the right triangle",
      },
    },
    "required": ["a", "b"],
  },
})
  response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo-0613",
    messages=messages,
    functions=functions,
    function_call="auto",
  )
  print(response)
  response_message = response["choices"][0]["message"]

  if response_message.get("function_call"):

    function_name = response_message["function_call"]["name"]
    fuction_to_call = available_functions[function_name]
    function_args = json.loads(response_message["function_call"]["arguments"])
    function_response = fuction_to_call(**function_args)
    print(f'function to call: {fuction_to_call}')

    messages.append(response_message)
    messages.append({
      "role": "function",
      "name": function_name,
      "content": function_response,
    })
    second_response = openai.ChatCompletion.create(
      model="gpt-3.5-turbo-0613",
      messages=messages,
    )
    return second_response


print(run_conversation())
