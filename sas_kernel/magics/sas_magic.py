#
# Copyright SAS Institute
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
from __future__ import print_function
import IPython.core.magic as ipym
import re

@ipym.magics_class
class SASMagic(ipym.Magics):
            
    @ipym.cell_magic
    def SAS(self,line,cell):
        '''
        %%SAS - send the code in the cell to a SAS Server

        This cell magic will execute the contents of the cell in a SAS
        session and return any generated output

        Example:
            %%SAS
            proc print data=sashelp.class;
            run;
            data a;
                set sashelp.cars;
            run;
        '''
        import saspy as saspy
        self.mva=saspy.SAS_session()
        self.mva._startsas()#path=self._path, version=self._version)
        
        res=self.mva.submit(cell,'html')
        output=self._clean_output(res['LST'])
        log=self._clean_log(res['LOG'])
        dis=self._which_display(log,output)
        return dis

    @ipym.cell_magic
    def IML(self):
        '''
        %%IML - send the code in the cell to a SAS Server
                for processing by PROC IML

        This cell magic will execute the contents of the cell in a
        PROC IML session and return any generated output. The leading 
        PROC IML and trailing QUIT; are submitted automatically.

        Example:
           %%IML
           a = I(6); * 6x6 identity matrix;
           b = j(5,5,0); *5x5 matrix of 0's;
           c = j(6,1); *6x1 column vector of 1's;
           d=diag({1 2 4});
           e=diag({1 2, 3 4});

        '''
        res=sas.submit("proc iml; "+ self.code + " quit;")
        output=_clean_output(res['LST'])
        log=_clean_log(res['LOG'])
        dis=_which_display(log,output)
        return line,dis

    @ipym.cell_magic
    def OPTMODEL(self):
        '''
        %%OPTMODEL - send the code in the cell to a SAS Server
                for processing by PROC OPTMODEL

        This cell magic will execute the contents of the cell in a
        PROC OPTMODEL session and return any generated output. The leading 
        PROC OPTMODEL and trailing QUIT; are submitted automatically.

        Example:
        proc optmodel;
           /* declare variables */
           var choco >= 0, toffee >= 0;

           /* maximize objective function (profit) */
           maximize profit = 0.25*choco + 0.75*toffee;

           /* subject to constraints */
           con process1:    15*choco +40*toffee <= 27000;
           con process2:           56.25*toffee <= 27000;
           con process3: 18.75*choco            <= 27000;
           con process4:    12*choco +50*toffee <= 27000;
           /* solve LP using primal simplex solver */
           solve with lp / solver = primal_spx;
           /* display solution */
           print choco toffee;
        quit;

        '''
        res=sas.submit("proc optmodel; "+ self.code + " quit;")
        output=_clean_output(res['LST'])
        log=_clean_log(res['LOG'])
        dis=_which_display(log,output)
        return dis

    def _which_display(self,log,output):
        lst_len=30762
        lines=re.split(r'[\n]\s*',log)
        i=0
        elog=[]
        debug1=0
        for line in lines:
            #logger.debug("In lines loop")
            i+=1
            e=[]
            if line.startswith('ERROR'):
                e=lines[(max(i-15,0)):(min(i+16,len(lines)))]
            elog=elog+e
        tlog='\n'.join(elog)
        if len(elog)==0 and len(output)>lst_len: #no error and LST output
            return HTML(output)
        elif len(elog)==0 and len(output)<=lst_len: #no error and no LST
            color_log=highlight(log,SASLogLexer(), HtmlFormatter(full=True, style=SASLogStyle))
            return HTML(color_log)
        elif len(elog)>0 and len(output)<=lst_len: #error and no LST
            color_log=highlight(tlog,SASLogLexer(), HtmlFormatter(full=True, style=SASLogStyle))
            return HTML(color_log)
        else: #errors and LST
            color_log=highlight(tlog,SASLogLexer(), HtmlFormatter(full=True, style=SASLogStyle))
            return HTML(color_log+output)

    def _clean_output(self,output):
        output = output.replace('\\n', chr(10)).replace('\\r',chr(ord('\r'))).replace('\\t',chr(ord('\t'))).replace('\\f',chr(ord('\f')))
        output=output[0:3].replace('\'',chr(00))+output[3:-4]+output[-4:].replace('\'',chr(00))
        return output

    def _clean_log(self,log):
        log    = log.replace('\\n', chr(10)).replace('\\r',chr(ord('\r'))).replace('\\t',        chr(ord('\t'))).replace('\\f',chr(ord('\f')))
        log=log[0:3].replace('\'',chr(00))+log[3:-4]+log[-4:].replace('\'',chr(00))
        return log

if __name__ == '__main__':
        from IPython import get_ipython
        get_ipython().register_magics(SASMagic)