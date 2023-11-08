import sqlite3
from flask import Flask, render_template, request, g, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
import time
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

UPLOAD_FOLDER = '/static/image'

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

DATABASE = 'social_media.db'
DEFAULT_PFP = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAfQAAAH0CAYAAADL1t+KAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAABxPSURBVHgB7d3Pi11n/QfwpyYyA5k2AxPIYAKBBDrWQCJtacCluq60G1fVnRvtxpW4Ki60+1Y3WfkPtLhX9wkoRAj9ARYiRhLIQNImkEi03+/n1pNOpvPj/jz3PJ/n9YLLnaZjzcy997zP5/N8znOeuXz58ucFAKja1woAUD2BDgAJCHQASECgA0ACAh0AEhDoAJCAQAeABAQ6ACQg0AEgAYEOAAkIdABIQKADQAICHQASEOgAkIBAB4AEBDoAJCDQASABgQ4ACQh0AEhAoANAAgIdABIQ6ACQgEAHgAQEOgAkINABIAGBDgAJCHQASECgA0ACAh0AEhDoAJCAQAeABAQ6ACQg0AEgAYEOAAkIdABIQKADQAICHQASEOgAkIBAB4AEBDoAJCDQASABgQ4ACQh0AEhAoANAAgIdABIQ6ACQgEAHgAQEOgAkINABIAGBDgAJCHQASECgA0ACAh0AEhDoAJCAQAeABAQ6ACQg0AEgAYEOAAkIdABIQKADQAICHQASEOgAkIBAB4AEBDoAJCDQASABgQ4ACQh0AEhAoANAAgIdABIQ6ACQgEAHgAQEOgAkINABIAGBDgAJCHQASECgA0ACAh0AEhDoAJCAQAeABAQ6ACQg0AEgAYEOAAkIdABIQKADQAICHQASEOgAkIBAB4AEBDoAJCDQASABgQ4ACQh0AEhAoANAAgIdABIQ6ACQgEAHgAQEOgAkcLQA1Tl69GhZWVkpa2trZXV1dfR1/Fk84p+774nHbo8fP/7K49GjR6Pn+/fvj54fPHgwegbqIdBh4CKUjx8/XtbX158K8Vn+e3sF/W5dwEe43717d/R1BD8wTAIdBibCdmNj40mIzxLes/494v8/HqdOnRr92cOHD0fhfu/evdGzgIfhEOgwAFF5b25uPgnxoYqTi/h7xiNEqG9vb5c7d+4Id1gygQ5LEhVwVL5DD/GDdBX8uXPnRi35mzdvqtxhSQQ69CwC/MyZM9WG+H5ibX9ra2v0dYT67du3Rw+gHwIdetBV4/EYZyCtdl3lHicuN27cULVDDwQ6LFBrQb5brLlH1d4N00W4C3ZYDIEOC9B6kO+2c5ju1q1bgh0WwJEG5kiQHy5CPdrxsb4ewQ7MhyMOzEkMu0V7eVnXjdckfkexvn7y5MlRqBueg9kJdJhRhNPzzz+fbmq9D90ae5wMacPDbAQ6zCBa61Fpaq/Ppltfj1DXhofpOArBFFTli9G14a9du6Zahwm5fSpMKKryF198UZgvSJwsvfTSS0/2jwfGo0KHMUVbPSpIQbN48buO7WQj3KMF71aucDiBDmOIYLlw4YIJ9p7FyVPceU4LHg6n5Q6HiAnsaLEL8+WI3/vFixdHrwOwP4EOB4gKMcLEFPtydaFuuQP2J9BhH7FeHuu4DEe8HvG6AF+l7IA9RHCoBoepC3TXq8PTVOiwS+xcJsyHLUI99gEAviTQYYcI89jYhOGLneWEOnxJoMP/CPP6CHX4kkCH8uWWo9QnQt3wIgh0GIW5yem6dTfJgZYJdJomCPKwLS+tE+g0K3Ye06rNJV5PO8rRKoFOk2LnsRiCI5/z58+XlZWVAq0R6DQntnF1o5W84vW1XS8tEug0J9ZahXlu8fqajaA1Ap2mxNCUwak2eK1pjUCnGaq29sTrbT2dVgh0mhHr5tZV2xKvt+FHWiHQaYJ183atr69rvdMEgU56Wu1ovdMCgU56whytd1og0EktbrjipiuEaL3bRY7MBDqpqc7ZKap0g5FkJdBJyyAcu8X7wYAcWQl0UooDt1Y7e4lAV6WTkUAnJdU5+4kwV6WTkUAnHdU5h1Glk5FAJx2DcBxGlU5GAp1Uojp3aRLjUKWTjUAnlQhza+eMQ5VONgKdVLTbmYRAJxOBThoxCKc6ZxJRpVuiIQuBThom25mGrg5ZCHRSiMo89uqGScX7xnAcGQh0UtA2ZRbW0slAoJOCAzKzcEJIBgKd6kW7fW1trcC0ou2+srJSoGYCneptbGwUmNXm5maBmgl0qifQmQdtd2on0Kma6XbmxbQ7tRPoVE1VxTzp9lAzgU7VVOfLdeXKlfLGG2+Ul19+uWxtbY2+fu+990qtnCBSM/0lqlbjAThC8N133y0ffPBB+eyzz8orr7xSXnvttfL666+Xmrzzzjujn2Onq1evjh43b94sb775ZqmNE0RqJtCpVqyf17Z3e5YQjCp898+xU/y7S5cujU5WahLvp1hHf/z4cYHaaLlTrWPHjpWajBOCEew1eP/99w/9njh5qZG2O7US6FSrtvZophAc58Tjww8/LDXSdqdWAp1q1VahZw7BvXz66aelRm7BS60EOtXKuN1rrSGYSW0nitAR6FQpBpdq2wTk2WefLVlk+ll26wbjoDYCnSrVWEW98MILh35PLVPhmX6WvWi7UyOBTpVqrKDGuSStlmvRM/0se9F2p0YCnSrVuH4eFetBQRj/LjaYqUGmn2UvKnRqdOTVV199q0BlTpw4UZ577rlSmwjC06dPj4bfYiOZWIv+9re/Xd5+++3qAjDTz7Lbw4cPy/b2doGaPHP58uXPC1TmW9/61ijUYREizK9fv16gJlruVMkUMot05MiRArUR6FRJoLNI1tCpkUCnSgId4GkCnSoJdBbJ+4saCXSq5IDLInl/USOBDgAJCHQASECgA0ACAh0AEhDoVOnx48cFFsX7ixoJdKrkgMsieX9RI4EOsItAp0YCnSrF3bD6dOXKlfLGG2+Ul19+uWxtbY2+fu+99wo5CXRqZPcEqtTnAfedd94p77777lN/dvXq1dEjbht60H3BqdN//vOfArVRoVOlvg64UYXvDvOd4t9FsJNL3x0gmAeBTpX6OuC+//77h35PVPDkouVOjQQ6Veor0Mepvj/88MNCLvfv3y9QG4FOlYZ0wP30009HD/JQoVMjgU6VHj16VPpw6tSpsb5vnNY89Xjw4EGB2gh0qhQVVB9t93ED/Y9//GMhh3hvqdCpkUCnWn203V955ZWxvi/W2n//+98X6mf9nFoJdKrVR9v90qVLY39vXMIW16VTN+12aiXQqdbdu3fLokWFPm6VHoNxP/3pTwt16+N9BYsg0KnWvXv3Sh9ef/31sb/3gw8+KL/+9a8Lk4sToli2WPYWu1ru1OrIq6+++laBCv33v/8tJ0+eLEePLnYH4xdeeKH86U9/Knfu3Bnr+69duzZ6nqRd37rYnOfnP//56Pccyxb//ve/R38eX8efhT5+nzFo+Y9//KNAjQQ6VVtbWxs9Fu3s2bMTXZrWbUgj1A8WHY0f/vCHo9DuQnwv8fuM3+W4Vx1MK07atre3C9RIoFO1qM5PnDhRFi2C5LPPPntSfY9DqB8s2usxcxC/13FEtT7J8sc04v/DUBy1soZO1fqspn72s59NXCHG5Lu93p8Wa+W/+MUvJp416GOLXQNx1EygU7XYAKSvg/Bzzz1Xfvvb35ZJRahHJeqSti8q4B/96EdT7ay36O11433U1w6EsAgCner1Ne0eYkDul7/8ZZlU7CQXE9sth/qVK1fKD37wg9G6+TTGvXxwWtbOqZ1Ap3q3b98uffrxj39c3nzzzTKpCPPvfve7oxZ8SzdziSCPFntU5uOul+9l0evn417FAEO12Ot9oAdxqVG0S9fX10tfYj39n//851St42jBx/8u/huLDqlliJOV6EjEUGA8zxLinTiBeu2118qixLXn2u3U7pnLly9/XqByZ86cGT36FpXnLHdaiyG73/zmNykm4aMSj5OVce4hP65os0eYL7rd/tFHH/Xe6YF5U6GTQrSzlxHob7/99uh52lDvhsQisKJirzXYY2J9njen6WYVFh3kHdPtZOA6dFKIXeOOHz9eVldXS9++//3vl2eeeWamyjSCPU4K4vHss8+OAq0G0V6PjWHmefvYmFGIqwkWvYlMJ8L8X//6V4HaCXTSiLX0zc3NsgxRSc4a6iHWm2PXtAj2mAaPcD99+nQZmmivx9/xrbfeKp988kmZh/hZf/WrX5Wf/OQnpU83btywmQwpWEMnle985zsL39v9IFGpRvt5npenRaUaJwzRCYjnuB6+b1GJx8lKPOJmKfMYdNspfsaoyvvuTMRJ4DzX/GGZBDqpLGs4bqcI80Vecx6h14V8PEdlG8/zquRjej8COzoEsTtbPC8y9OLniDBfxomKYTgyEeikEtV5BMQyq/SObV8PFiciMcEea+bLENV57M3vcjWysLEMqcRWsEPZjS2m1v/85z+X733ve4UvdUEev5tlhXmw1SvZuGyNdCLQowU9hCo9/h6/+93vRgNkUa23uvVrhHjMAMRGOt/85jeX0l7fLYbhIBMtd1Iawlr6XloL9qjEo0MxtMvwbt26VT7++OMCmQh0UhrSWvpesgd7VOTRmehrY5hJWDsnK2vopDSktfS9xL7ksYYcO83VsonMuCLE//CHPwwyzENMtQtzMlKhk1ZU5y+++OJSdo+bVFwaFlunxuVhtVbtfe27PgvXnZOZQCe12A724sWLpSaxOU13t7Ihh3s36LbMDW8m5bpzMhPopHfhwoVeb606TxHqsc1qPEcVP+8d2iYVwR03kInnIVfiezEIR3YCnfSi5R6t96EOyE0iQj2q9m4Xt9iSNUI+nudVzUflHdV2XHIXj1jjj8dQLjebVpwYWTsnM4FOEyKYzp07V2hTXHPuunOyM+VOE6J6dc/rNsUgnDCnBQKdZsT6aVzORjvi9Y5rzqEFAp1mqNTaE6+3dXNaIdBpSrTeW91PvTVea1oj0GlOVG1RrZOXbgwtEug0J9ZV//a3v1lPT6rbq93rS2sEOk2Kg/7169cL+cRucNbNaZFAp1n37t0rf//73wt5xOsZryu0SKDTtBiastaaQ7yOhuBomUCneYKgfnaCA4EOI9GqdReuOsXrJsxBoMMTbq1Zn3i94nUDBDo8RajXQ5jD0wQ67BIhoYU7bDHzIMzhafXfIBoWoAv0M2fOFIbFABzsTYUO+4jQcJ36sMTrIcxhbyp0OEC0du/fv1+2trbK6upqYTliG9fY2c+mMbA/FTocIkIk9n53Q5fliN/7X/7yF2EOhxDoMIYIlb/+9a82oOlZ/L7j925vdjicljuMKdq+sYYb4R7DckeP+vgsSvyu7eAHk3FEgglFyGxvb5cLFy5YV1+Au3fvumMaTEHLHaYQVfrVq1dNXM9R1wGJeQVhDpNTocMMItBjx7JowZ88ebIwHVU5zE6gw4yiWo8wilCKYNeGH1/3uzPBDrMT6DAnUanvrNYF+/6ivR6zCPGIr4HZCXSYM234/QlyWByBDgvQtZIj3CPYjx8/3nTFLshh8QQ6LFAX7BHmEeqtrbELcuiPQIceRLDHI1rx0YaPx/r6eskqBgSjO2HYDfoj0KFn3fBcV7WfOnWqrK2tldpFiEeAq8ZhOQQ6LMnOqj3CfWNjY/SoqXLvQvzWrVuuIYclE+gwABHs3VpzV7lHsA9tmC7+nl2Ix/a3KnEYDoEOA7Ozcg8R6MeOHRsFfDxHe76PG8PE3yHuBR+VdxfiAhyGS6DDwHUBHxVxJwI9wj2eu4BfWVkZPe9+7Bah3AVz/He7f47g3hniwhvqItChQhG23QT5zqAH2uVuawCQgEAHgAQEOgAkINABIAGBDgAJCHQASECgA0ACAh0AEhDoAJCAQAeABAQ6ACQg0AEgAYEOAAkIdABIQKADQAICHQASEOgAkIBAB4AEBDoAJCDQASABgQ4ACQh0AEhAoANAAgIdABI4WoBqHD16tKysrJTV1dUnjyNHjoz+PL6O5xBf7+fhw4dfeX706FF5/Pjx6Oud/wzUQ6DDQEVwr6+vl7W1tdHX8XxQUI+r+28c9t/qwv3Bgwfl7t27T74Ghkmgw0AcP358FNobGxuj567aXpauAxAnFadOnRr9WVTt9+/fL9vb26Pne/fuFWAYBDosSQT2yZMnBxPg44i/YwR8PEIEfFTvEfDxHK16YDkEOvQoWuebm5ujarwLxZpFwJ84cWL0CFG13759u9y5c0e4Q88EOizYzko8Q4gfJDoN8Th37two3G/evKlyh54IdFiQqMLPnDmTPsT3E8G+tbU1+joq9qjcozUPLIZAhzmKajwGyOJRw5p4X7q2fEzK37hxQ9UOC+CIA3MQ0+DRVhfkB4vfU1e137p1axTugh3mw5EHZnDs2LFy+vTpUZgzmRgOjIdgh/kQ6DCFqDTPnj37ZLqb6Ql2mA+BDhOIdnpMcKvI50+ww2wEOozBsFt/umCPUI/L3uwpD+NxZIJDRDUeVbkg71dc8he/+wj2uOQNOJgjFOwjBt4iyFu9jnwIuqn46Ixcv35dGx4OINBhl669HhUiwxCb1Fy6dGlUrccD+CqBDjvE7m5REc7jNqXMX9eG/+ijj9zpDXYR6FC+qMojLLrbhDJccbJ18eLF0cBcVOuG5uALAp3mxVr5+fPnVeWViZOvuOHNtWvXrK3D//tagYZFKLz00kvCvFLxusXaunkHUKHTqAiC559/3gR7EhHoMf8Qa+uqdVqlQqc5ceC/cOGCME8mXs9YW4/XF1ok0GlKtNjjoK/FnlM3MKcFT4u03GmCPdjbEoG+srJSPvnkE1PwNEOgk15UbdFiV5W3JfaDjza8KXhaoeVOanFJmjBvV9eCj/cBZCfQSSva69bLidc/Lk20aRDZabmTUqyhGoxip+6OefaCJysVOukIc/bjvUFmKnRSiRurmGTnIN0E/Mcff1wgE4FOCtFKjZ3fTpw4UeAwMQEf75kIdZe1kYWWO9WLA3NMsgtzJhHvl3jfxPsHMhDoVK0L87W1tQKTiveNUCcLgU61hDnzINTJQqBTJWHOPAl1MhDoVEeYswhCndoJdKojzFkUoU7NBDpVievMhTmLFO+vs2fPFqiNQKcabn9KX+I69djXAGoi0KlC7O7l5hr0KULdNrHURKAzePbfZlm896iJQGfQosXugMoyxfvPUg81EOgM1rFjx0br5rBs8T6M9yMMmUBnkFZXV8v58+ddPsQgxPsw3o9xlzYYKoHO4HQbx0Sow1A4yWToBDqDE5cLCXOGyDXqDJlAZ1BiAMltUBkyl7MxVAKdwdjY2HCgpArxPo33KwyJQGcQosUe27pCLeL9akiOIRHoLF03BGfYiJp0k+/etwyFQGfpon1pCI4axZCcZSKGQqCzVLE/uz3aqZn3MEMh0FmaqMpVN2QQ72Pr6SybQGdprJuThfV0hkCgsxSxN7Z1czKxns6yCXR6F3eusuZIRvG+Pn78eIFlEOj0yro52cX16VrvLINAp1cuUSO7eH/H/QigbwKd3kSrPR6QXdyPwLISfRPo9EKrnda4lI2+CXR6odVOa2Id3f0J6JNAZ+G02mnV+vq61ju9EegslFY7rYv3v6l3+iDQWSitdloXYW7qnT4IdBZGqx2+EFPvNpxh0QQ6C6PVDl+y4QyLJtBZCK12eFp8HgzIsUgCnbkzCAd7c206iyTQmbuzZ88WYG+uTWdRBDpzFUNwMQAE7C2uTd/Y2CgwbwKdudJqh8OdO3fOgBxzJ9CZG4NwMB4DciyCQGcuDMLBZCLQDcgxTwKduRDmMJloufvcME8CnZlFdW5HOJjc5uamHeSYG4HOzOxTDdNTpTMvAp2ZRGUel+EA04nPjyqdeRDozER1AbPzOWIeBDpTi+rcZWowu6jSzaEwK4HO1FQVMD8+T8xKoDMV1TnMl81mmJVAZyqqCZi/+FzZEpZpCXQmpjqHxYgwV6UzLYHOxFTnsDgR6Kp0piHQmYjqHBZLlc60BDoTUZ3D4qnSmYZAZ2yqc+hHhLnr0pmUQGdsqnPoj7Y7kxLojEV1Dv1yF0MmJdAZi+oc+ifQmYRA51AbGxuqc1gCd2JjEgKdQ1nLg+XRHWNcAp0DRWXufuewPKp0xiXQOZDqAJbPWjrjEOjsy5QtDMPm5qaNZjiUQGdf3/jGNwowDGZZOIxAZ18nTpwowDDYDpbDCHT2ZCMZGBbbwXIYgc6etPdgeGJPCNiPQOcrjh07VtbW1gowLC5h4yACna84ffp0AYbJbAv7Eeg8xaVqMGzx+TQcx14EOk/RzoNhMxzHfgQ6T7EzHAyf4Tj2ItB5Iqpzl6rB8BmOYy8CnSdie0mgDobj2E2g84Q2HtTDcBy7CXRGHBygLvF5dRLOTgKdEVOzUB+fW3YS6IwG4WLIBqhLfG511ugIdEzLQsXcd4GOQMe151AxJ+R0BHrj4kYsrj2HerkmnY5Ab5wbsUD9zMAQBHrjnNlD/ayjEwR6w2z1CjnEpLuTcwR6w2z1CnnYChaB3jBn9JCHTWYQ6I3SbodctN0R6I3Sbod8tN3bJtAb5Uwe8tF2b5tAb5DNZCAnbfe2CfQGabdDXjaZaZdAb5AzeMjLPdLbJdAbE632tbW1AuQUn++VlZVCewR6Y1TnkJ9p9zYJ9MaYgoX8tN3bJNAbEhOwBmYgv/icx+edtgj0hmi3Qzt83tsj0BtiXQ3aoRvXHoHeEGfs0A7zMu0R6I2wOxy0JdbQXaLaFoHeCO03aI+uXFsEeiNcxgLt8blvi0BvhAod2hMtd5evtUOgN0DbDdoUYR7zM7RBoDfA5WrQLt25dgj0BjhDh3bp0LVDoCdnu1dom21g2yHQk1OdA44DbRDoyVk/BxwH2iDQk3NmDjgOtEGgJ2f9HHA9ehsEemKmW4HgevQ2CPTE3JgB6Dge5CfQE7OPM9Cx/JafQE/MGTnQsQSXn0BPKtbLDMEAnTgerKysFPIS6EmpzoHdtN1zE+hJCXRgN8eF3AR6UtbLgN0cF3IT6Ek5Ewd2s8FMbgI9IWfhwH5WV1cLOQn0hFTnwH6c8Ocl0BMS6MB+bAGbl0BPyAcW2I8T/rwEekI+sMB+DMblJdCTUZ0DhzEYl5NAT0Z1DhzGiX9OAj0ZgQ4cxnEiJ4GejDNv4DCOEzkJ9GSceQOHcZzISaAnEpOrpleBw7iVak4CPRFtNGBcqvR8BHoiPqDAuFy6lo9AT8QHFBiXjl4+Aj0RH1BgXAqAfAR6IlruwLgcL/IR6EmYcAcm4ZiRj0BPQrsdmJS2ey4CPQln2sCkFAK5CPQkrIcBk1Kh5yLQk3CmDUzKbnG5CPQktNyBSens5SLQk/DBBCal5Z6LQE/A5SfANBw7chHoCVgHA6alSs9DoCfgAwlMS0GQh0BPQKAD03L8yEOgJ+ADCUzL8SMPgZ6AlhkwrSNHjhRyEOgJmFIFpuWS1zwEegI+kMC0FAR5CPQEfCCBaVlDz0OgV86HEZiVOZwcBHrlfBCBWX39618v1E+gV067HZiVuzXmINArp+UOQBDolVOhA7NSGOQg0CvngwjMyixODgK9cnZ5AmZlKC4HgV45LXdgVir0HAR65bTcgVkpDHIQ6JXzQQRm5TiSg0CvnA8iMCvHkRwEesW024F5sY5eP4FeMRPuAHQEesW0yYB50fGrn0AHQIGQgECvmDNqYF4Eev0EOgAkINArpkIH5sXxpH4CHQASEOgVs+YFzIvr0Osn0Csm0AHoCHQASECgV0yLDJgXQ3H1E+gAkIBAB4AEBHrFDMUB86LlXj+BXjGBDkBHoANAAgIdABIQ6ACQgECvmCEWYF7M5NRPoAMg0BMQ6ACQgEAHgAQEOgAkINABIAGBDgAJCHQASECgA0ACAh0AEhDoAJDA/wEnCffncMc03wAAAABJRU5ErkJggg=="

# HELPER FUNCTIONS
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def check_password(saved_password, entered_password):
    return check_password_hash(saved_password, entered_password)

# MAIN SITE STUFF
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/content-rules")
def contentrules():
    return render_template("content-rules.html")

@app.route('/post', methods=['GET', 'POST'])
def post():
    if not "user_id" in session:
        return redirect("/register")

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        dataURL = request.form['dataURL']
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO posts (content,authorid,title,imageData,postdate) VALUES (?,?,?,?,?)', (content,session["user_id"],title,dataURL,time.time()))
        db.commit()
        return redirect("/")
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM posts')
    posts = cursor.fetchall()
    return render_template('posts.html', posts=posts)

@app.route("/browse")
def browse():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts ORDER BY id DESC limit 50")
    posts = cursor.fetchall()
    return render_template("browse.html",posts=posts)

@app.route("/post/<post_id>")
def post_page(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT content, authorid, title, imageData, postdate, id, username FROM posts INNER JOIN users ON posts.authorid = users.userid WHERE id = ?",(post_id,))
    post = cursor.fetchone()
    #print(post)
    #cursor.execute("SELECT userid, username FROM users WHERE userid = ?",(post[1],))
    #author = cursor.fetchone()
    cursor.execute("SELECT commentid, comment_content, postdate, authorid, username FROM comments INNER JOIN users ON comments.authorid = users.userid WHERE postid = ? ORDER BY commentid DESC",(post_id,))
    comments = cursor.fetchall()

    if post:
        #title, content, authorid, imageData = post
        date = datetime.fromtimestamp(post[4])

        return render_template("post.html", post=post,postdate=date.strftime("%d-%m-%y"),comments=comments)
    
    return render_template("error.html")

@app.route("/users/<user_id>")
def user_page(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT username, userid, description, joindate, ismoderator, profilepicture FROM users WHERE userid = ?",(user_id,))
    user = cursor.fetchone()

    cursor.execute("SELECT * FROM posts WHERE authorid = ? ORDER BY id DESC limit 50",(user_id,))
    posts = cursor.fetchall()
    #print(post)

    if user:
        #title, content, authorid, imageData = post
        date = datetime.fromtimestamp(user[3])

        return render_template("user.html", user=user, joindate=date.strftime("%d-%m-%y"), posts=posts)
    
    return render_template("error.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # Hash the password securely
        hashed_password = generate_password_hash(password)

        # Store the user's information in the 'users' table
        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO users (username, email, password_hash, description, joindate, profilepicture) VALUES (?, ?, ?, ?, ?, ?)',
                       (username, email, hashed_password, "User has no description.",time.time(),DEFAULT_PFP))
        db.commit()

        # Redirect to a new page or perform additional actions
        # (e.g., a 'Thank you for registering' page or login page)
        return render_template('register_success.html')
    return render_template('registration.html')  # Replace with your registration form template

@app.route('/login',methods=["GET","POST"])
def login():
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT userid, username, password_hash, ismoderator FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        if user:
            user_id, saved_username, saved_password, ismoderator = user

            if check_password(saved_password, password):
                session["user_id"] = user_id
                if ismoderator and ismoderator > 0:
                    session["moderator"] = True
                return redirect("/")
        
        return "Invalid username or password. Please try again."
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('user_id',default=None)
    session.pop('moderator',default=None)
    return redirect("/")

@app.route("/comment/<post_id>", methods=['POST'])
def comment(post_id):
    comment_content = request.form["comment-box"]
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO comments (postid, authorid, comment_content, postdate) VALUES (?, ?, ?, ?)",(post_id, session["user_id"], comment_content, time.time()))
    db.commit()
    return redirect("/post/" + str(post_id) + "#comments")

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if not "user_id" in session:
        return redirect("/register")

    if request.method == "POST":
        desc = request.form["desc"]
        pfp = request.form["dataURL"]
        print(desc)

        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET description = ?, profilepicture = ? WHERE userid = ?",(desc, pfp, session["user_id"]))
        db.commit()

        return redirect("/users/" + str(session["user_id"]))

    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE userid = ?",(session["user_id"],))
    user_info = cursor.fetchone()

    return render_template("settings.html",user_info=user_info)

# END OF MAIN SITE STUFF

#API STUFF
@app.route("/api/is_logged_in")
def is_logged_in():
    if 'user_id' in session:
        return { "response" : True, "userid" : session["user_id"]}
    else:
        return { "response" : False}

@app.route("/api/user/<user_id>")
def user_api(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT username, description, joindate FROM users WHERE userid = ?",(user_id,))
    user = cursor.fetchone()

    if user:
        username, description, joindate = user

        return {"username" : username, "description" : description, "joindate" : joindate}

    return {"response" : "Error!"}

@app.route("/api/post/<post_id>/delete", methods=['GET'])
def delete_post(post_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?",(post_id,))
    post = cursor.fetchone()
    if post:
        if session["user_id"] == post[2] or session["moderator"] > 0:
            print("epic")
            cursor.execute("DELETE FROM posts WHERE id = ?",(post_id,))
            db.commit()
            return "Go back to browse idiot"
    return "Friggin heck"

# END OF API STUFF

if __name__ == '__main__':
    app.run(debug=True,port=5100)
