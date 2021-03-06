NEUROML2_PATH = "/Users/rgerkin/NeuroML2" # Path to NeuroML2 compliant OSB models.  

# Standard library.  
import os

# Installed packages.  
import sciunit
from neuronunit import neuroelectro,tests,capabilities
from neuronunit.neuroconstruct import models
import osb

osb_projects = osb.get_projects(1)

# Initialize the test with summary statistics from the reference data
# and arguments for the model (model).  

from pythonnC.utils.putils import OSB_MODELS
brain_areas = os.listdir(OSB_MODELS)
models_tested = 0
nlex_ids = {}
for brain_area in brain_areas:
	path = os.path.join(OSB_MODELS,brain_area)
	if not os.path.isdir(path):
		continue
	neuron_types = os.listdir(path)
	for neuron_type in neuron_types:
		path = os.path.join(OSB_MODELS,brain_area,neuron_type)
		if not os.path.isdir(path):
			continue
		model_names = os.listdir(path)
		for model_name in model_names:
			path = os.path.join(OSB_MODELS,brain_area,neuron_type,model_name,"neuroConstruct")
			if not os.path.isdir(path):
				continue
			
			if model_name in ['korngreen-pyramidal',
							  'IzhikevichModel',
							  'RothmanEtAl_KoleEtAl_PyrCell']:
				continue
			#if models_tested not in [11,17]:
			#	models_tested += 1
			#	continue
					
			print("\r\r*** %d: %s ***\r\r" % (models_tested,model_name))
			models_tested += 1
			identifier = model_name#.lower()
			project = osb.get_project_with_identifier(identifier,projects=osb_projects)
			if project is None:
				print("No OSB project identifier found for model %s" % model_name)
				continue
			
			neurolex_ids = project.NEUROLEX_IDS_CELLS
			if not neurolex_ids or not len(neurolex_ids):
				print("No neurolex ids found for model %s" % model_name)
				continue
			if ';' not in neurolex_ids:
				neurolex_id = neurolex_ids
			else:
				print("Multiple neurolex ids found; skipping...")
				continue
			print("Neurolex ID is %s" % neurolex_id)
			if neurolex_id in nlex_ids:
				nlex_ids[neurolex_id] += 1
			else:
				nlex_ids[neurolex_id] = 1
			print(brain_area,neuron_type,model_name)
			
			if model_name in ['MainenEtAl_PyramidalCell']: # Number 12 hangs.  
				print("Skipping model %s" % model_name)
				continue
			
			model_info = (brain_area,neuron_type,model_name)

			# Initialize (parameterize) the model with some initialization parameters.
			model = models.OSBModel(*model_info)

			# Specify reference data for this test.  
			reference_data = neuroelectro.NeuroElectroSummary(
				neuron = {'nlex_id':neurolex_id}, # Neuron type.  
				ephysprop = {'name':'Resting Membrane Potential'}) # Electrophysiological property name.  

			# Get and verify summary data for the combination above from neuroelectro.org. 
			if reference_data.get_values() is None:
				print("Unable to get the reference data from NeuroElectro.org.")
				continue  
			
			test = tests.RestingPotentialTest(
				observation = {'mean':reference_data.mean,
					  			  'std':reference_data.std})

			# (1) Check capabilities,
			# (2) take the test, 
			# (3) generate a score and validate it,
			# (4) bind the score to model/test combination. 

			score = test.judge(model,stop_on_error=True)

			# Summarize the result.  
			print("=========\r"*3)
			score.summarize()
			print("=========\r"*3)
			
			# Get model output used for this test (optional).
			vm = score.related_data

# Neuroelectro successful for: 
# 9,11,13,17 

# Neuroelectro cell not found for:
# 10,14,15 (sao2128417084)

# Neuroelectro NES not found for:
# 6 (BAMSC1042)
# 16 (nifext_52)
