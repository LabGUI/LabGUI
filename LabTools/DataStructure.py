import numpy as np
import logging
from pprint import pprint as pp

COMPLEX_HDR = "complexvalues#"
REAL_HDR="realvalues#"


class LabeledData(object):
    """ This class contains two attributes a n by m matrix and a m element list which labels the colums of the matrix"""
    def __init__(self,data=None,labels=None,fname=None,dataset_name=""):
        		
        self.data = data
        self.labels = labels
        self.dataset_name = dataset_name
        
        if not fname == None:
            "If fname is included, it will overwrite data and labels arguments and replace them with the data and labels of the fname"
            self.load_from_file(fname)
        
        else:
            
            self.nlines=np.size(data,0)
            self.ncols=np.size(data,1)
            self.nlabels=np.size(labels)
            
            if self.ncols == self.nlabels:       
            
                self.data=data
                self.labels=labels
            elif self.nlines == self.nlabels:
                
                self.data=np.transpose(data)
                self.labels=labels
                
            else:
                logging.error("There is %i labels for %i columns in the data matrix"%(self.nlabels,self.ncols))

        
    def display(self):

        print("#####---LabeledData---#####")
        print("There is %i lines and %i columns"%(self.nlines,self.ncols))
        print("The labels are")
        pp(self.labels)    
        print("The data is")
        pp(self.data)
        print("#####-----------------#####")

    def save_to_file(self,fname):
        """this method will save the data into a folder with the labels as header """
        
        header_txt=""

        for l in self.labels:
            header_txt="%s\t%s"%(header_txt,l)        
        
        if np.iscomplex(self.data).any():
            #prepare the header line with the labels
            header_txt = COMPLEX_HDR + header_txt
            np.savetxt(fname,self.data.view(float),header=header_txt)
        else:
            header_txt = REAL_HDR + header_txt
            np.savetxt(fname,self.data,header=header_txt)
        
        
    def load_from_file(self,fname=None):
            """this method will load the data and labels from a file"""
        
            filestream =  open(fname, "r")
            #read the headerline
            labels=filestream.readline()
            #get rid of the "# " at the beginning and the "\n" at the end
            labels=labels[2:-1].split("\t")
            filestream.close()

            #the first string of the line describes whether the format of the values is complex or real     
            if labels[0] == COMPLEX_HDR:
                labels.pop(0)
                data = np.loadtxt(fname).view(complex)
            elif labels[0] == REAL_HDR:
                labels.pop(0)
                data=np.loadtxt(fname)
            else:
                #in that case we assume the value is readable by numpy.loadtxt
                data = np.loadtxt(fname)

            self.nlines=np.size(data,0)
            self.ncols=np.size(data,1)
            self.nlabels=np.size(labels)
            
            if self.ncols == self.nlabels:       
            
                self.data=data
                self.labels=labels
                
            elif self.nlines == self.nlabels:
                
                self.data=np.transpose(data)
                self.labels=labels
            else:
                    logging.error("There is %i labels for %i columns in the data matrix"%(self.nlabels,self.ncols))
                    
                    
            """here we can call an external function that will look for an attribute for the dataset_name and assign it or give the name None"""
            """Was a bit confused by this one -> I'm assuming that you meant a way to access a way that will distinguish the different files loaded
                Using date as a marker"""
#            self.dataset_name= get_dataset_name(fname=fname)
            self.dataset_name=fname
        
    def lines(self):
        """this method will return the lines in an array"""
        return np.squeeze(np.array([l for l in self.data])) 

    def columns(self):
        """this method will return the columns in an array"""
        return np.squeeze(np.array([c for c in np.transpose(self.data)]))
        
    
    def __getitem__(self,inargs):
        """"override the [] operator in order to be able to call self[usual indexation,column label]"""
        logging.debug(inargs)
        
        #if there is only two arguments it means the first one is a conventional index reference and the second one is a column label
        if np.size(inargs) == 2:
            if isinstance(inargs[0],slice) or isinstance(inargs[0],int):
                index = inargs[0]
                label = inargs[1]
            else:
                index = inargs[1]
                label = inargs[0]
            
            #check if the label is in our list of labels
            if label in self.labels:
                label_index=self.labels.index(label)
            else:
                #if the label is an index or something like ":", "1:", ":3" and "1:4" we consider that one used the normal matrix indexing
                if isinstance(label,int) or isinstance(label, slice):
                    label_index = label
                else:
                    logging.warning("The indexing variable %s doesn't have a match in the possible indexes, it is therefore ignored"%(label))
                    label = None
                
        elif np.size(inargs) == 1:

            #testing whether the argument is a slice or an index
            if isinstance(inargs,slice) or isinstance(inargs,int):
                index = inargs
                label = None
            else:
                #if not one of the latter, check if the label is in our list of labels
                label = inargs
                index = None
                if label in self.labels:
                    label_index=self.labels.index(label)
                else:
                    label=None
        
        #just normal indexing
        if label == None and not index == None:
            answer = self.data[index]
        
        #normal indexing as first argument and label indexing as second argument
        elif not label == None and not index == None:
            answer = self.data[index,label_index]
            
        elif not label == None and index == None:
            answer = self.data[:,label_index]
        
        else:
            logging.error("Unexpected situation, arguments were :")
            logging.error(index)
            logging.error(label)
        
        if isinstance(answer,np.ndarray):
#            print "This is a numpy array"
#            print np.size(answer)
#            print "before",answer
            if np.size(answer) == 1:
                answer = answer[0]
            else:
                answer=np.squeeze(answer)
#            print "after",answer
        else:
            print("this is not a numpy array")
        
        return answer
        

def test_labels_class_LabeledData(labels=["a","b","c"]):
    mydat=LabeledData(np.array([[1,2,3],[4,5,6],[7,8,9]]),labels)  

    mydat.display()

    num_test=6
    test_passed=0    
    
    if (mydat[0:2]==np.array([[1,2,3],[4,5,6]])).all():
        logging.info("the indexing with a slice for the first argument alone works")
        test_passed+=1
        
    if (mydat[labels[0]] == np.array([1,4,7])).all():
        logging.info("the indexing by label in first argument alone works")
        test_passed+=1
        
    if (mydat[:,labels[1]] == np.array([2,5,8])).all():
        logging.info("the indexing by label in second argument with a slice for the first argument works")
        test_passed+=1
        
    if mydat[1,labels[1]] == 5:
        logging.info("the indexing by label in second argument with a index for the first argument works")
        test_passed+=1
    
    if (mydat[-1] == np.array([7, 8, 9])).all():
        logging.info("the negative indexing by index in first argument alone works")
        test_passed+=1    
        
    mydat.save_to_file("test_fonction.txt")
    
    mydat_duplicate=LabeledData(fname="test_fonction.txt")
    
    if (mydat.data == mydat_duplicate.data).all() and (mydat.labels == mydat_duplicate.labels):
        logging.info("the save to file and reload the same instance works")
        test_passed+=1 
    else:
        print mydat.display()
        print mydat_duplicate.display()
    
#    mydat
    print("test passed : %i over %i"%(test_passed,num_test))
      
if __name__=="__main__":
    
#    test_labels_class_LabeledData(labels=[1.1,2.3,3.5])
#    ex = LabeledData(fname = "C:\\Users\\User\\Documents\\AcousticBlackHole\\GuiTools\\test2.txt")
    test_labels_class_LabeledData()
#    ex = LabeledData(fname="C:\\Users\\User\\Desktop\\08032016_PIEZOCHARACTERIZATION_PZT1\\meta_data_first_day.metadata")#"C:\Users\User\Documents\AcousticBlackHole\meta_data_change_pressure.metadata")
#    test_labels_class_LabeledData()
#    ex = LabeledData(fname="C:\Users\User\Documents\AcousticBlackHole\meta_data_change_pressure.metadata")

