import os,sys,base64
from pathlib import Path
from ipykernel.kernelbase import Kernel
from .import jinter

canvasnum = 1

class JKernel(Kernel):
    implementation         = 'jkernel'
    implementation_version = '3.2.0'
    language_info          = { 'name': 'J', 'mimetype': 'text/J', 'file_extension'  : 'ijs' }
    banner                 = 'J Programming Language - Jupyter Kernel'
    help_links             = [
        {
            'text': 'Vocabulary',
            'url':  'http://www.jsoftware.com/help/dictionary/vocabul.htm'
        },
        {
             'text': 'NuVoc',
            'url':  'http://www.jsoftware.com/jwiki/NuVoc'
        }
    ]

    def __init__(self, *args, **kwargs):
        super(JKernel,self).__init__(*args,**kwargs)

        JInsFol = os.getenv('J_INSTALLATION_FOLDER', f'{os.getenv("CONDA_PREFIX")}/share/j901')
        JBinFol = os.getenv('J_BIN_FOLDER', f'{JInsFol}/bin')
        self.J = jinter.J(JInsFol,JBinFol)

        # Initialize J JHS
        self.J.Exec('IFJHS_z_ =: 1')
        self.J.Exec('canvasnum_jhs_ =: 1')
        self.J.Exec('load \'jhs\'')

        # This one is not defined on Windows ???
        if os.name == 'nt': self.J.Exec('iad_pplatimg_ =: 15!:14@boxopen')

        # Get J user folder
        self.J.Exec('tmpstr_jinter_ =: jpath \'~user\'')
        self.J.JUsrFol = Path(self.J.GetStrVar('tmpstr_jinter_'))

    def _retr(self,output, silent):
        global canvasnum
        if silent: return
        content = { 'source': 'J', 'metadata': {}, 'data': {} }
        if output.startswith('<!-- j html output a -->'):
            try:
                prefix = '<!-- j html output a --><img'
                if output.startswith(prefix):
                    # Extract image name
                    stapos = output.find('src=')
                    imgnam = output[stapos+11:]
                    imgnam = imgnam[:imgnam.find('?')]
                    imgnam = self.J.JUsrFol/'temp'/imgnam

                    # Read image in base64 encoded data
                    with open(imgnam,'rb') as fp: imgdat = base64.b64encode(fp.read()).decode()
                    imgnam.unlink(missing_ok=False)

                    # Send output data
                    content['data']['image/png'] = imgdat
                    #self.log.error(repr(content))
                    self.send_response(self.iopub_socket, 'display_data', content)

                # Other output (plot)
                else:
                    htmnam = self.J.JUsrFol/'temp'/'plot.html'

                    # Read html file
                    with open(htmnam,'r') as fp:
                        htmdat = fp.read() \
                                .replace('</article>', '</article><script>graph();</script>') \
                                .replace('canvas1', f'canvas{canvasnum}')
                    htmnam.unlink(missing_ok=False)

                    canvasnum += 1
                    content['data']['text/html'] = htmdat
                    self.send_response(self.iopub_socket, 'display_data', content)

            except Exception as e:
                content = { 'name': 'stdout', 'text': f'JKernel: Internal Error.\n{e}\n' }
                self.send_response(self.iopub_socket,'stream',content)

        # Is it an html output
        elif output.startswith('<html>'):
            content['data']['text/html'] = output
            self.send_response(self.iopub_socket, 'display_data', content)
        else:
            # Normal text output
            content = { 'name': 'stdout', 'text': output }
            self.send_response(self.iopub_socket,'stream',content)

    def do_execute(self, code, silent, *args, **kwargs):
        global canvasnum

        # Pass input to J (new version)
        # Multi-line statements (like verb definitions) are now possible
        # Only the output of the last line (statement) is printed
        lines = [line for line in code.splitlines() if line.strip()]
        lastline = ''
        # Check last line (end of multiline statement)
        if lines:
            lastline = lines.pop().strip()
            if not lastline == ')': code = '\n'.join(lines)

        code = code.replace("'","''")
        self.J.Exec(f"input_jinter_ =: '{code}'")
        self.J.Exec('0!:110 input_jinter_')

        # Process last line (receive output)
        if lastline:
            self.J.Exec(lastline)
            output = self.J.Recv()
            if output: self._retr(output, silent)

        return {
            'status':           'ok',
            'execution_count':  self.execution_count,
            'payload':          [],
            'user_expressions': {},
        }

    def do_shutdown(self,restart): pass
    def do_inspect(self,code,cursor_pos,detail_level=0): pass

if __name__ == '__main__':
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=JKernel)

