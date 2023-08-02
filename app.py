from flask import Flask, request, jsonify
import base64
from PIL import Image
from io import BytesIO
import numpy as np
import pandas as pd 
from flask_cors import CORS 
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def get_upe_data():
   UPE_data_path="data/UPE_data.csv"
   UPE_data=pd.read_csv(UPE_data_path)
   return UPE_data


def get_csv_files(name,rank,quota,category):
  user_name = name
  user_category = category
  user_rank = int(rank)  # Correct column name for rank input
  user_quota = quota
  UPE_data=get_upe_data()
  # print(f"category:{user_category} user_rank:{user_rank} user_quota:{user_quota}")
  # Filtering data based on user's category and quota
  if(user_quota=="All India"):
    filtered_data = UPE_data[(UPE_data['Quota'] == user_quota)]
  else:
    filtered_data = UPE_data[(UPE_data['Category'] == user_category) & (UPE_data['Quota'] == user_quota)]
  # Selecting rows based on user's rank
  selected_rows = filtered_data[(filtered_data['Opening Rank'] <= user_rank) & (filtered_data['Closing Rank'] >= user_rank)]

  # If user's rank is smaller than the opening rank, include that row too
  additional_rows = filtered_data[filtered_data['Opening Rank'] > user_rank]

  # Concatenate selected rows and additional rows
  output_data = pd.concat([selected_rows, additional_rows])

  # Sort the output data based on 'Opening Rank' in increasing order
  output_data = output_data.sort_values(by='Opening Rank')

  top_5_institutes = output_data['Institute Code'].unique()[:5]
  top_5_data = output_data[output_data['Institute Code'].isin(top_5_institutes)]


  # Store only the top 5 unique Institute codes and Institute names in the "TOP 5 Insti" folder
  top_5_insti_data = top_5_data[['Institute Code', 'Institute']].drop_duplicates()

  return output_data, top_5_data, top_5_insti_data


def image_to_base64(path):
    image = Image.open(path)
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def generate_html_content(name, rank, quota, category,top_5_data,  top5_institutes, all_colleges,path):
    logo_base64 = image_to_base64(path)
    # The rest of your code, but replace the logo src with the base64 string:
    logo_src = f"data:image/png;base64,{logo_base64}"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: white;
            }}
            .container {{
                max-width: 794px; /* A4 width in pixels */
                margin: 0 auto;
                padding: 20px;
                box-sizing: border-box;
            }}
            h2 {{
                color: #0066cc;
                margin-bottom: 10px;
            }}
            p {{
                line-height: 1.5;
                margin-bottom: 10px;
                text-align:left;
            }}
            table {{
                border-collapse: collapse;
                width: 100%;
                font-size: 12px;
                border: 1px solid #ddd;
            }}
            th, td {{
                text-align: left;
                padding: 5px 8px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .logo {{
                float: right;
                margin-right: 20px;
                margin-top: 35px;
            }}
            .logo_bottom {{
                text-align: center;
                margin-right: 20px;
                margin-top: 35px;
            }}
            .youtube_img {{
                text-align: center;
            }}
            toggle-button {{
                cursor: pointer;
                background-color: #0066cc;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
                margin-top: 5px;
            }}
            .print-button {{
                cursor: pointer;
                background-color: #e60000; /* Red background color */
                color: white; /* White font color */
                border: none;
                padding: 10px 20px; /* Slightly enlarged padding */
                font-size: 16px; /* Slightly enlarged font size */
                margin-left: 10px;
                border-radius: 8px; /* Add rounded corners */
            }}
            .result-content table {{
                margin-top: 30px;
                width: 100%;
                border-collapse: collapse;
            }}

            .result-content th,
            .result-content td {{
                padding: 8px;
                text-align: left;
                border: 1px solid #ddd;
            }}

            .result-content th {{
                background-color: #f2f2f2;
            }}

            /* Apply alternating light and dark shades to table rows */
            .result-content tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .result-content tr:nth-child(even) {{
                background-color: #f9f9f9; /* Light shade */
            }}

            /* Apply a dark shade to odd table rows */
            .result-content tr:nth-child(odd) {{
                background-color: #e6e6e6; /* Dark shade */
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <img src={logo_src} alt="<b>PrefRANK</b> Logo" width="279" height="106.2">
            </div>
            <h2>Hey {name}
            <button class="print-button" onclick="window.print()">Print</button>
            </h2>
            <p>We are absolutely elated to see that you've chosen to use our <b>PrefRANK</b> Model to generate your counseling report for UPSEE 2023. It's a delightful surprise to have you on board! 😊</p>
            <p>Before we dive into your report, we request you to join out Whatsapp community for further updates about your personalized college comparison reports.</p>
            <p>Whatsapp community link here: <a href="https://chat.whatsapp.com/Hqluy4ZajJOHHuoU3qO7xn">https://chat.whatsapp.com/Hqluy4ZajJOHHuoU3qO7xn</a></p>
            <p>Based on the inputs you provided, including your rank '{rank}', quota {quota}, and category {category}, our amazing model, trained on the 2022 UPSEE Counseling data, has come up with some incredible results! You have an outstanding chance of securing a spot in the following top 5 colleges:</p>
            <p>Drumroll, please! Here they are:</p>
            {top5_institutes.to_html(index=False).replace('Institute Code', 'Institute Code').replace('.0', '')}
            <p></p>
            <p>We can't help but feel thrilled for you! But wait, the excitement doesn't end there. Let's dive into the treasure trove of branches that await you at these colleges:</p>
            <p>Branches Available:</p>
            {top_5_data.to_html(index=False).replace('Institute Code', 'Institute Code').replace('.0', '')}
            <p></p>
            <div class="darker-section">
            <p>But hold on, there's even more good news! The list doesn't end with these top 5 colleges; there's a world of possibilities out there just waiting for you to explore. Here's an extensive list of all the colleges where you stand a chance of getting admission based on your rank, quota, and category:</p>
            <p>List of Colleges:</p>
            </div>
            {all_colleges.to_html(index=False).replace('Institute Code', 'Institute Code').replace('.0', '')}
            <p></p>
            <p>Isn't this journey exhilarating? We're so excited to be part of this adventure with you! 🌟</p>
            <p>Stay tuned for the forthcoming comparison reports on your top 5 colleges. These reports will provide you with invaluable insights to help you make the best decision for your future.</p>
            <p>Oh, and if you truly enjoyed using our <b>PrefRANK</b> Model and found it helpful, we kindly request you to support us by liking our YouTube video (<a href="https://www.youtube.com/watch?v=7LolXy8yDM0&ab_channel=JanmejayPratapSingh">link here</a>) and sharing it among your peers. Your support means the world to us and will go a long way in covering our operating costs. 😇</p>
            <div class="youtube_img">
            <a href="https://www.youtube.com/watch?v=7LolXy8yDM0">
                <img src="https://img.youtube.com/vi/7LolXy8yDM0/0.jpg" alt="Youtube Video Thumbnail">
            </a>
            </div>
            <p>If you ever have any questions or if something catches you by surprise, please don't hesitate to reach out to us at <a href = "mailto: pref.rankk@gmail.com">pref.rankk@gmail.com</a>. We're here to support you every step of the way!</p>
            <p>With warmest regards and excitement,</p>
            <p><b>PrefRANK</b> - Team</p>
            <div class="logo_bottom">
                <img src={logo_src} alt="<b>PrefRANK</b> Logo" width="279" height="106.2">
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

def append_to_google_sheet(user_info):
    # Define the scope
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

    # Load the credentials from the json key file
    creds = ServiceAccountCredentials.from_json_keyfile_name('prefrank-3a38577833e0.json', scope)

    # Create a client to interact with the Google Drive API
    client = gspread.authorize(creds)

    # Open the file using its name
    sheet = client.open('Website responses').sheet1

    # Append the data to the sheet
    sheet.append_row(user_info)

app = Flask(__name__)
CORS(app)

@app.route('/generate_html', methods=['POST'])
def generate_html():
    print("came here")
    data = request.json  # Get the input data from the request
    # Extract data from the request
    name = data.get('name')
    rank = data.get('rank')
    quota = data.get('quota')
    category = data.get('category')
    email=data.get('email')
    phone=data.get('phone')
    output_data, top_5_data, top_5_insti_data = get_csv_files(name, rank, quota, category)  # Use the correct arguments
    top_5_insti_data = top_5_insti_data.drop_duplicates(subset=['Institute Code']).head(5)
    output_data = output_data.drop(columns=['Opening Rank', 'Closing Rank'])
    top_5_data = top_5_data.drop(columns=['Opening Rank', 'Closing Rank'])
    logo_path = "images/logo.png"
    # Generate the HTML content for this user (same as before)
    html_content = generate_html_content(name, rank, quota, category, top_5_data, top_5_insti_data, output_data,
                                         logo_path)
    
    # return jsonify({'html_content': html_content})
    user_info = [name, email, phone, rank, category, quota]
    append_to_google_sheet(user_info)
    # Appending data to the file
    # with open('users.txt', 'a') as file:
    #     file.write(user_info)
    return jsonify(html_content=html_content)

@app.route('/test',methods=['GET'])
def hello():
   print("Testing route working")
   return 'hello'

@app.route('/',methods=['GET'])
def homepage():
   print("Testing route working")
   return 'hello from main'

if __name__ == '__main__':
    app.run(port=5001,debug=False)  # Change 5001 to any available port number

