from . import *  
from app import leetcode_data
from app.irsystem.models.helpers import *
from app.irsystem.models.helpers import NumpyEncoder as NumpyEncoder
from app.irsystem.models.search import *

project_name = "Leethelper"
net_id = "Jiejun Zhang, jz2252; Keyang Yu, ky442; Shuyi Gu, sg2474; Wei Cheng, wc655; Tan Su, ts864"

@irsystem.route('/', methods=['GET'])
def search():
	query = request.args.get('search')
	if not query:
		data = []
		output_message = ''
	else:
		output_message = "Your search: " + query
		similarity_score_list = compute_cosine_similarity(query,leetcode_data)
		similarity_score_list = sorted(enumerate(similarity_score_list), key=lambda x:x[1][1], reverse=True)
		# return_data = similarity_score_list[:5]
		return_data = [x[1] for x in similarity_score_list[:5]]
	return render_template('search.html', name=project_name, netid=net_id, output_message=output_message, data=return_data)



