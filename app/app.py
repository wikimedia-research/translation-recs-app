from flask import Flask, render_template
import pandas as pd
import os
from rec_util import get_dummy_recs
app = Flask(__name__)




@app.route('/')
def home():
    return 'Contribution Recommendations'

    
@app.route('/translation')
def translation_recommendations(user=None):

    # should get target language from user, for now set to french
    target = 'fr'


    # The username comes from the home page and should be passed to this function.
    user = 'ellery' 

    #recs is a list of enwiki article titles. For now the function returns a dummy list. 
    recs = get_dummy_recs(target, user=user)

    return render_template('translation_recs.html', recs=recs)

   
    
if __name__ == '__main__':
    app.debug = True

    app.run()
