from flask import Flask, request, jsonify, render_template_string
import google.generativeai as genai
import json
import re

app = Flask(__name__)

GOOGLE_API_KEY = "AIzaSyCmWPv4aC9HU1rFOnyxd5qXfV4YPLJItV4"
GUIDE_URL = "https://docs.google.com/document/d/1QLumD13Xp71w1r_T8jLhaBveS20qGMTItfhFhPBsdWw/edit?usp=sharing"

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def analyze_and_correct_code(code, language):
    prompt = f"""You are an expert in all programming languages and code analysis. Please analyze the following code, which is written in {language} and then correct it, if there is any errors, and add a comment in the corrected code of what you corrected. If the code is syntactically correct, then provide sample execution output without any other details.
       Code:
       {code}
        """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"


def generate_code(comment, language):
    prompt = f"Convert the following comment to {language} code, providing only essential comments. Remove all the non essential comments and also remove all markdown code block indicators: {comment}"
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"
def get_file_extension(language):
     prompt = f"What is the correct file extension for the programming language {language}? Just return the file extension and nothing else."
     try:
         response = model.generate_content(prompt)
         return response.text.strip()
     except Exception as e:
        return f"Error: {e}"

html_template = """
<!DOCTYPE html>
<html lang="en" class="dark-theme">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CXR</title>
    <style>
        body {
            font-family: sans-serif;
            margin: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
             background: linear-gradient(to bottom right, #000000, #000030);
            color: #d4d4d4;
           transition: background 0.5s ease;
        }
        .dark-theme {
           background: linear-gradient(to bottom right, #000000, #000030);
        }
          .light-theme{
           background: linear-gradient(to bottom right, white, #ADD8E6);
             color: black;
           }


        header {
            text-align: center;
            padding: 20px;
              color: #fff;
              text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            font-family: Arial, sans-serif;
        }
        .light-theme header {
            color: black;
        }
         header h1 {
            text-align: center;
            margin: 0;
            flex: 1;
            font-size: 2.5em;
             font-weight: 600;
            font-family: Arial, sans-serif;
        }
        main {
            flex: 1;
            display: flex;
            padding: 20px;
            gap: 20px;
        }
         .code-editor, .generated-code {
            flex: 1;
            display: flex;
            flex-direction: column;
            position:relative;
         }

        .code-editor > label,
        .generated-code > label {
            margin-bottom: 5px;
            display: block;
            color: #d4d4d4;
             padding-left: 10px;
        }
         .light-theme .code-editor > label,
        .light-theme .generated-code > label {
             color: black;
           }
       .code-area {
         flex: 1;
          padding: 10px;
          border: 1px solid #406180;
          border-radius: 4px;
           background-color: #252525;
            color: #d4d4d4;
            transition: background 0.3s ease, color 0.3s ease, border-color 0.3s ease;
        }
        .light-theme .code-area {
           background-color: #f0f0f0;
            color: black;
         }
        .code-area:focus{
          outline: none; /* Remove the default focus outline */
         box-shadow: 0 0 5px #406180;
         }
         .generated-code > div{
             display: flex;
            justify-content: space-between;
          }
        footer {
            padding: 20px;
            text-align: center;
            transition: background-color 0.3s ease;
            background: rgba(0,0,0,0.4);
            margin-top: 10px;
             display: flex;
            justify-content: space-between;
             align-items:center;
             position: relative;
        }

        footer button, #runButton {
           padding: 10px 15px;
            background-color: #406180;
            color: #fff;
            border: 1px solid white;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            flex: 1;
             margin: 0px;
              font-size: 16px;
        }
        footer button:hover, #runButton:hover {
            background-color: #1e3a5d;
         box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
         transform: translateY(-2px);
       }
         .light-theme footer button, .light-theme #runButton {
            background-color: #ADD8E6;
           color: #000000;
         }
      .light-theme footer button:hover, .light-theme #runButton:hover {
         background-color: #1e3a5d;
       }

          #languageSelect {
             padding: 10px;
             background-color: #252525;
            color: #d4d4d4;
            border: 1px solid #406180;
            border-radius: 4px;
             margin-bottom: 20px;
              transition: background-color 0.3s ease, color 0.3s ease;
             width: 200px;
           }
        .light-theme #languageSelect {
            background-color: #ADD8E6;
            color: black;
         }
          #runButton {
            line-height: 0;
             position: absolute;
            bottom: 0;
            left: 10px;
            width: calc(100% - 20px);
            height: 40px;
        }
     #themeButton {
          padding: 10px;
          background-color: #406180;
         color: #fff;
         border: none;
           border-radius: 4px;
          cursor: pointer;
            transition: background-color 0.3s ease;
         }
          #themeButton:hover {
        background-color: #1e3a5d;
         box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
         transform: translateY(-2px);
       }
      .light-theme #themeButton {
            background-color: #ADD8E6;
            color: black;
        }
       .light-theme #themeButton:hover {
         background-color: #1e3a5d;
       }
     #footer-buttons {
            display: flex;
            justify-content: space-between;
             width: 100%;
            position: absolute;
             bottom: 0;

         }
       #footer-buttons > button {
           padding: 10px 15px;
            background-color: #406180;
            color: #fff;
            border: 1px solid white;
            border-radius: 4px;
            cursor: pointer;
            transition: background-color 0.3s ease;
            flex: 1;
             margin: 0px;
              font-size: 16px;
           height: 40px;

        }
       #footer-buttons > button:hover {
            background-color: #1e3a5d;
           box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
           transform: translateY(-2px);
        }
          .light-theme #footer-buttons > button:hover{
            background-color: #1e3a5d;
        }
        .modal {
            display: none; /* Hidden by default */
            position: fixed; /* Stay in place */
            z-index: 1; /* Sit on top */
            left: 0;
            top: 0;
            width: 100%; /* Full width */
            height: 100%; /* Full height */
            overflow: auto; /* Enable scroll if needed */
            background-color: rgba(0,0,0,0.4); /* Black w/ opacity */
        }

        .modal-content {
            background-color: #252525;
            margin: 15% auto; /* 15% from the top and centered */
            padding: 20px;
            border: 1px solid #406180;
            width: 50%; /* Could be more or less, depending on screen size */
             color: #d4d4d4;
            border-radius: 5px;
        }
        .light-theme .modal-content{
          background-color: white;
            color: black;
        }
        .modal-content > input[type="text"] {
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #406180;
            border-radius: 4px;
            background-color: #333;
             color: #d4d4d4;
            width: calc(100% - 22px);
            transition: background-color 0.3s ease, color 0.3s ease;
        }
           .light-theme .modal-content > input[type="text"]{
             background-color: #f0f0f0;
              color: black;
           }
          .modal-content > input[type="text"]:focus{
          outline: none; /* Remove the default focus outline */
         box-shadow: 0 0 5px #406180;
         }

        .modal-content > button {
            padding: 10px 15px;
             background-color: #406180;
             color: #fff;
            border: 1px solid white;
             border-radius: 4px;
           cursor: pointer;
              transition: background-color 0.3s ease;
              margin-right: 5px;
        }
         .modal-content > button:hover {
            background-color: #1e3a5d;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
           transform: translateY(-2px);
        }
        .light-theme .modal-content > button{
             background-color: #ADD8E6;
             color: #000000;
        }
          .light-theme .modal-content > button:hover {
            background-color: #1e3a5d;
        }
        .close {
            color: #aaaaaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
             cursor: pointer;
        }

        .close:hover,
        .close:focus {
            color: #fff;
            text-decoration: none;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <header>
        <h1>CXR</h1>
          <div>
           <select id="languageSelect">
                  </select>
             <button id ="themeButton">Theme</button>
        </div>
    </header>
    <main>
        <div class="code-editor">
            <label for="codeInput">Input :</label>
            <textarea id="codeInput" class="code-area"></textarea>
             <button id="runButton">Run</button>
        </div>
        <div class="generated-code">
            <label for="generatedCode">Output :</label>
            <textarea id="generatedCode" class="code-area" readonly></textarea>
              <div id ="footer-buttons">
                <button id="downloadButton">Download</button>
                <button id="clearButton">Clear</button>
                <button id="guideButton">Guide</button>
             </div>
        </div>
    </main>
     <div id="customLangModal" class="modal">
       <div class="modal-content">
         <span class="close">×</span>
           <label for="customLangInput">Enter Custom Language:</label>
           <input type="text" id="customLangInput" placeholder="Language Name">
            <button id="customLangSubmit">Submit</button>
        </div>
    </div>
    <footer>
    </footer>
    <script>
      document.addEventListener('DOMContentLoaded', () => {
          const languageSelect = document.getElementById('languageSelect');
          const codeInput = document.getElementById('codeInput');
          const generatedCode = document.getElementById('generatedCode');
          const clearButton = document.getElementById('clearButton');
          const downloadButton = document.getElementById('downloadButton');
           const guideButton = document.getElementById('guideButton');
          const runButton = document.getElementById('runButton');
            const footerButtons = document.getElementById('footer-buttons');
             const themeButton = document.getElementById('themeButton');
            const body = document.body;

          const customLangModal = document.getElementById('customLangModal');
         const customLangInput = document.getElementById('customLangInput');
         const customLangSubmit = document.getElementById('customLangSubmit');
         const modalCloseButton = document.querySelector('.close');
          let currentLanguage = 'python';


          const languages = ["python", "javascript", "java", "c++", "csharp", "c", "go", "rust", "ruby", "r", "kotlin", "mysql", "other"];
           languages.forEach(lang => {
               const option = document.createElement('option');
              option.value = lang;
              option.text = lang;
              languageSelect.appendChild(option);
             });
          languageSelect.value = 'python';

         let isDarkTheme = true;

           themeButton.addEventListener('click', () => {
                isDarkTheme = !isDarkTheme;
              if(isDarkTheme){
                  body.classList.add('dark-theme');
                  body.classList.remove('light-theme');
               }
              else{
                   body.classList.add('light-theme');
                   body.classList.remove('dark-theme');
               }
           });
         languageSelect.addEventListener('change', (event) =>{
            if(event.target.value === 'other'){
                customLangModal.style.display = "block";
            }
           else {
                 currentLanguage = event.target.value;
            }
        });
        customLangSubmit.addEventListener('click', () =>{
            currentLanguage = customLangInput.value;
             customLangModal.style.display = "none";
        })
         modalCloseButton.addEventListener('click', () => {
                customLangModal.style.display = "none";
            });

         window.addEventListener('click', (event) => {
                if (event.target === customLangModal) {
                    customLangModal.style.display = "none";
                }
        });


          runButton.addEventListener('click', async () => {
              const code = codeInput.value.trim();
              if (!code) {
                   generatedCode.value = ""
                   return;
                }
              try {
                 let data = null;
                 if (code.startsWith('//')){
                   const response = await fetch('/generate', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ code: code, language: currentLanguage}),
                   });
                  if (!response.ok) {
                     const errorData = await response.json();
                       throw new Error(`API Error: ${response.status} - ${errorData.error || 'Unknown error'}`);
                  }
                   data = await response.json();
                   if(data) {
                      if (data.generatedCode) {
                          generatedCode.value = data.generatedCode;
                        }
                    }
                 }
                 else{
                      const response = await fetch('/analyze', {
                       method: 'POST',
                       headers: { 'Content-Type': 'application/json' },
                       body: JSON.stringify({ code: code, language: currentLanguage}),
                     });
                     if (!response.ok) {
                         const errorData = await response.json();
                         throw new Error(`API Error: ${response.status} - ${errorData.error || 'Unknown error'}`);
                     }
                     data = await response.json()
                     try{
                         const parsedData = JSON.parse(data.generatedCode);
                          if (parsedData.message){
                            generatedCode.value = parsedData.message + "\\n" + (parsedData.output || "");
                         }
                         else{
                             generatedCode.value = parsedData.code
                         }
                    }
                    catch(e){
                         generatedCode.value = data.generatedCode;
                    }
                 }


              } catch (error) {
                generatedCode.value = `Error: ${error.message}`;
               }
          });


          clearButton.addEventListener('click', () => {
              codeInput.value = '';
              generatedCode.value = '';
          });
            downloadButton.addEventListener('click', async () => {
                const code = generatedCode.value;
               let fileExtension = '';
               if(currentLanguage !== "other") {
                   if(currentLanguage === 'python') {
                      fileExtension = "py"
                     } else if (currentLanguage === 'javascript'){
                       fileExtension = "js"
                     } else if (currentLanguage === 'java'){
                       fileExtension = 'java'
                     }
                     else if (currentLanguage === 'c++'){
                       fileExtension = 'cpp'
                     }
                      else if (currentLanguage === 'csharp'){
                       fileExtension = 'cs'
                     }
                     else if (currentLanguage === 'c'){
                       fileExtension = 'c'
                     }
                     else if (currentLanguage === 'go'){
                      fileExtension = 'go'
                     }
                     else if (currentLanguage === 'rust'){
                      fileExtension = 'rs'
                     }
                     else if (currentLanguage === 'ruby'){
                      fileExtension = 'rb'
                    }
                    else if (currentLanguage === 'SQL' || currentLanguage === 'mysql'){
                      fileExtension = 'sql'
                    }
                    else if (currentLanguage === 'kotlin'){
                       fileExtension = 'kt'
                    }
                     else if (currentLanguage === 'r'){
                       fileExtension = 'r'
                    }
                }
               else{
                fileExtension = await get_file_extension(currentLanguage);
                }

                const fileName = `project.${fileExtension}`;
                const blob = new Blob([code], { type: "text/plain" });
                 const a = document.createElement('a');
               a.href = URL.createObjectURL(blob);
                a.download = fileName;
                 a.click();
            });
        guideButton.addEventListener('click', () => {
            window.open('""" + GUIDE_URL + """', '_blank');
        });
      });
    </script>
</body>
</html>
   """

@app.route('/', methods=['GET'])
def index():
    return render_template_string(html_template)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    comment = data.get('code')
    language = data.get('language')

    if not comment or not language:
        return jsonify({'error': 'Code and language are required'}), 400

    output = generate_code(comment, language)
    return jsonify({'generatedCode': output})

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    code = data.get('code')
    language = data.get('language')

    if not code or not language:
        return jsonify({'error': 'Code and language are required'}), 400
    output = analyze_and_correct_code(code, language)
    return jsonify({'generatedCode': output})


if __name__ == '__main__':
    app.run(debug=True, port=5001)
