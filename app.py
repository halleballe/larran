from flask import Flask, render_template, request, session, g, redirect, url_for
import sys
app = Flask(__name__)