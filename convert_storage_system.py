import sqlite3
import re
import base64

DATABASE = 'social_media.db'

# HELPER FUNCTIONS
def get_db():
	db = getattr(g, '_database', None)
	if db is None:
		db = g._database = sqlite3.connect(DATABASE)
	return db

def sanitize_filename(filename):
	# Replace characters that are not allowed in filenames with underscores
	sanitized_filename = re.sub(r'[\\/*?:"<>|]', '_', filename)
	# Remove leading and trailing whitespaces
	sanitized_filename = sanitized_filename.strip()
	# Limit the filename length to 255 characters (maximum allowed by most filesystems)
	sanitized_filename = sanitized_filename[:255]
	return sanitized_filename

def data_url_to_image(data_url, output_path):
	# Extract image data and format from the data URL
	match = re.match(r'data:image/([^;]+);base64,(.*)', data_url)
	if not match:
		print(data_url)
		print("Invalid data URL")
		return
	
	image_format = match.group(1)
	image_data = match.group(2)
	
	# Decode the base64-encoded image data
	decoded_image = base64.b64decode(image_data)
	
	# Determine the image file extension based on format
	if image_format == "jpeg":
		extension = "jpg"
	else:
		extension = image_format
	
	# Save the decoded image data to a file
	output_file = output_path + "." + extension
	with open(output_file, 'wb') as f:
		f.write(decoded_image)
	
	print("Image saved successfully at:", output_file)
	return output_file

if __name__ == "__main__":
	db = sqlite3.connect(DATABASE)
	cursor = db.cursor()
	cursor.execute("SELECT * FROM posts")
	posts = cursor.fetchall()
	for post in posts:
		if not post[4].find("data:") == -1:
			sanitized_name = str(post[0])
			img_path = "/" + data_url_to_image(post[4],"static/image/posts/" + sanitized_name)
			cursor.execute("UPDATE posts SET imageData = ? WHERE id = ?",(img_path,post[0],))
			db.commit()