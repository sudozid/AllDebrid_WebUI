from flask import Flask, render_template, request, make_response
import requests
import re

API_KEY=""
API_SHOWCASE=""

app = Flask(__name__)

def magnetcheck(input_text):
    if not re.match(r"^magnet:\?xt=.*$", input_text):
        return False

def processing(url):
    # this is thingy that will be returned to flask
    returnlist = []
    try:
        #Check instant availablity
        base_url = "https://api.alldebrid.com/v4"

        payload = {"agent": API_SHOWCASE,"apikey": API_KEY,"magnets[]":url}

        data = requests.get(base_url+"/magnet/instant",params=payload).json()

        if data['status'] == "success":
            if data['data']['magnets'][0]['instant']==True:
                #upload the magnet
                output = requests.get(base_url+"/magnet/upload",params=payload).json()
                #obtain the hash of the returned data
                hash = output['data']['magnets'][0]['hash']
                #obtain the intermediate link
                output = requests.get(base_url+"/magnet/status",params=payload).json()
                magnets = output['data']['magnets']



                for magnet in magnets:
                    if magnet['hash']==hash:
                        for attributes in magnet['links']:
                            payload['link']=attributes['link']
                            output = requests.get(base_url+"/link/unlock",params=payload).json()
                            output = output['data']
                            unlockedlink = dict(unlockedlink=output['link'], filename=output['filename'],
                                                size=output["filesize"])
                            returnlist.append(unlockedlink)
                        return returnlist
    except requests.exceptions.RequestException as e:
        return "Error: {}".format(e)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    input_text = request.form['text']
    if magnetcheck(input_text)==False:
        return render_template('index.html',error="Error: The input is not a valid magnet link.")

    processed_text = processing(input_text)

    response = make_response(render_template('index.html', links=processed_text))
    response.headers['Content-Type'] = 'text/html'

    return response

if __name__ == '__main__':
    app.run()
