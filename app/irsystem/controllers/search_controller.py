from . import *  
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder

project_name = "Coding Problems Hint Generator"
net_id = "Jiejun Zhang, jz2252; Keyang Yu, ky442; Shuyi Gu, sg2474; Wei Cheng, wc655; Tan Su, ts864"

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		data = range(5)
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=data)



