# Prompt 1 Defining Specs To GPT 4o

Please generate an impressive and nicely designed GUI for generating images from prompts in a repo. 

My openAI key is OPENAI_KEY in the dot env file

The GUI should allow the user to specify a title for the image and a prompt and a size that the image should be in pixels 

The user should also be able to specify where the generated image should be stored in their OS 

his setting should persist through reboots, so it will be to be saved into some kind of non-volatile storage 

Once the user has entered the prompt and any other parameters that they might wish to adjust, the generation request is sent to the DALLE API 

The file should be saved into a subfolder immediately within the output directory that the user specified. 

The subfolder should be in the format ddmmyy. 

If it does not already exist, it should be created 

he file name is the title that the user configured If the user chose a title "Smiling sloth at computer" the file name would be smiling-sloth-at-computer.webp 

The GUI should be nicely designed with clear buttons and a bright UI