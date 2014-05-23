import argparse, os, glob, subprocess, sys

pj,bn = os.path.join, os.path.basename

parser = argparse.ArgumentParser(description = 'Correct formant.txt files based on plotmish logs')
parser.add_argument('formant_files', help = 'directory containing formant.txt files or a single formant.txt file to be corrected')
parser.add_argument('-l','-logs', metavar = 'plotmish logs',default = 'log' , help = 'change folder containing plotmish correction logs. Can also be a single csv file. Default is log/')
parser.add_argument('-c','-corrected', metavar = 'corrected csvs', default = 'corrected', help = 'change folder to write corrected formant.txt files to, default is corrected/')
args = parser.parse_args()

if os.path.isdir('plotmish'):
    os.chdir('plotmish')

## get log files
if os.path.isdir(args.l):
	logs = glob.glob(pj(args.l, '*'))
else:
	logs = [args.l]

## get formant.txt files to be corrected
if os.path.isdir(args.formant_files):
	oldF = glob.glob(pj(args.formant_files,'*'))
else:
	oldF = [args.formant_files]

## make directory to write out files if it doesn't exist
if not os.path.isdir(args.c):
	subprocess.call(['mkdir', args.c])

## iterate over all log files
for l in logs:
	
	name = bn(l).rsplit('-',1)
	
	## check that file is named correctly
	if name[1] != 'corrLog.csv':
		print >> sys.stderr, 'Log file %r does not end in -corrLog.csv.  File may have been renamed \nskipping...' %bn(l)
		continue

	oldForms = []
	for o in oldF:
		formName = bn(o).rsplit('-',1)
		try: 
			oldForms += [o] if formName[0] == name[0] and formName[1] == 'formant.txt' else []
		except: pass

	##check that file corresponds to a formant.txt file
	if not oldForms:
		print >> sys.stderr, 'Log file %r does not correspond to a formant.txt file in %r \nskipping...' %(bn(l),bn(args.formant_files))
		continue

	## extract old formant files info to a list
	oldFile = open(oldForms[0],'rU')
	formList = [o.replace('\n','').split('\t') for o in oldFile.readlines()]
	oldFile.close()

	## extract logFile info to a list
	logFile = open(l,'rU')
	logList = [o.replace('\n','').split(',') for o in logFile.readlines()]
	logFile.close()
	## correct formant files
	for ll in logList[1:]:
		number = int(ll[0])
		time = ll[4]
		maxForms = ll[7]
		F1 = ll[9]
		F2 = ll[11]
		try:
			comment = ll[12]
		except:
			comment = 'corrected'
		## change the values where appropriate
		formList[number+2][3] = F1 if F1 != 'NA' else formList[number+2][3]
		formList[number+2][4] = F2 if F2 != 'NA' else formList[number+2][4]
		formList[number+2][9] = time if time != 'NA' else formList[number+2][9]
		formList[number+2][35] = maxForms if maxForms != 'NA' else formList[number+2][35]
		
		## add appropriate note
		reason = comment.split()[0].replace(':','').strip()
		try: 
			note = comment.split()[1].strip()
		except: 
			note = ''
		try:
			formList[number+2][38] = reason
			formList[number+2][38] = note
		except:
			formList[number+2] += [reason,note]

	## write to new formant.txt file
	newFile = open(pj(args.c,name[0]+'-formant.txt'),'wb')
	for i,fl in enumerate(formList):
		if i<2: 
			newFile.write(' '.join(fl)+'\n')
		else:
			newFile.write('\t'.join(fl)+'\n')
	newFile.close()