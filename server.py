# pip install flask flask-cors yt-dlp ; also install ffmpeg
# run: python server.py   (then set API_URL in clipscutter.html)
import os,re,glob,shutil,subprocess,tempfile
from flask import Flask,request,send_file,abort
from flask_cors import CORS
app=Flask(__name__);CORS(app)
@app.get('/clip')
def clip():
    v=request.args.get('id','');f=request.args.get('format','mp4')
    if not re.fullmatch(r'[\w-]{11}',v) or f not in('mp4','mp3'):abort(400)
    try:s=int(request.args['start']);e=int(request.args['end']);h=int(request.args.get('quality','360p').rstrip('p'))
    except Exception:abort(400)
    if e<=s:abort(400)
    d=tempfile.mkdtemp()
    cmd=['yt-dlp','--download-sections',f'*{s}-{e}','--force-keyframes-at-cuts','-o',os.path.join(d,'clip.%(ext)s')]
    cmd+=['-x','--audio-format','mp3'] if f=='mp3' else ['-f',f'bv*[height<={h}]+ba/b[height<={h}]','--merge-output-format','mp4']
    r=subprocess.run(cmd+['https://youtu.be/'+v],capture_output=True)
    out=glob.glob(os.path.join(d,'clip.'+f))
    if r.returncode or not out:shutil.rmtree(d,True);abort(500)
    resp=send_file(out[0],as_attachment=True,download_name='clip.'+f)
    resp.call_on_close(lambda:shutil.rmtree(d,True))
    return resp
if __name__=='__main__':app.run('0.0.0.0',5000)
