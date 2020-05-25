import React, { Component } from 'react'
import './App.css'
import 'axios'
import Axios from 'axios'
export class App extends Component {

  constructor(props) {
    super(props)
    this.state = {

      information: "",
      uploadProgress: {},
      title: "",
      max_lines: 0,
      copy_headers: true,
      sheet_name: "",
      count_headers: true,
      docfile: null,
      link: ""
    }
  }

  canUpload = () => {
    if (this.state.title.length > 0 && this.state.max_lines != 0 && this.state.docfile != null) return true;
    return false;

  }

  sendRequest = () => {

    const file = this.state.docfile
    console.log(this.canUpload());
    if (!this.canUpload()) {
      this.setState({
        error: true,
        message: "Please provide the right parameters"
      });
      return;
    }

    this.setState({
      error: false,
      information: "Splitting, please wait...",
      link: "",
    });


    const formData = new FormData();
    formData.append("docfile", file, file.name);
    formData.append("title", this.state.title);
    formData.append("max_lines", this.state.max_lines);
    formData.append("copy_headers", this.state.copy_headers);
    formData.append("count_headers", this.state.count_headers);
    formData.append("sheet_name", this.state.sheet_name);

    const liveServer = "/api/document/";
    const localServer = "http://localhost:8000/api/document/"
    const server = liveServer;
    const request = Axios.post(server, formData);

    request.then((e) => {
      window.document.getElementById('file').value = null
      // this.fileInputRef.current.value = null;
      console.log(e);
      this.setState({
        information: "Click the link below to download " + this.state.title,
        link: e.data['data'],
        error: false,

        oldTitle: this.state.title,
        title: "",
        max_lines: 0,
        copy_headers: true,
        sheet_name: "",
        count_headers: true,
        docfile: null,
      }, () => console.log(this.state));
    });
    request.
      catch((e) => {
        console.log(e)
        this.setState({
          error: true,
          message: e.response.data['data'],
          information: ""
        });
      });
  }


  fileListToArray(list) {
    const array = [];
    for (var i = 0; i < list.length; i++) {
      array.push(list.item(i));
    }
    return array;
  }

  onFilesAdded = (event) => {
    const files = event.target.files;
    const array = this.fileListToArray(files)
    this.setState({
      ...this.state,
      docfile: array[0]
    });
  }

  openFileDialog = (event) => { }

  render() {
    console.log(this.state);
    return (
      <div className="container" >
        <div className="form" >
          <div className="app-info" >
            ExcelSplit
        </div>
          {
            this.state.information.length == 0 ? null :
              <div className="information" >
                {this.state.information}
              </div>
          }
          {
            this.state.link.length == 0 ? null :
              <div className="information" >
                <a className="link" href={this.state.link}>Download {this.state.oldTitle} File </a>
              </div>
          }
          {
            this.state.error !== true ? null :
              <div className="information error" >
                {this.state.message}
              </div>
          }
          <div className="form-input" >
            <input value={this.state.title} className="text-input" placeholder="Title" type="text" onChange={(event) => {
              this.setState({
                title: event.target.value,
                error: false
              });
            }} />
          </div>

          <div className="form-input" >
            <input value={this.state.max_lines} className="text-input" placeholder="Max Lines per document" type="number" onChange={(event) => {
              this.setState({
                max_lines: event.target.value,
                error: false
              });
            }} />
          </div>


          <div className="form-checkbox " >
            <input defaultChecked={true} onChange={(event) => {
              this.setState({
                copy_headers: event.target.checked,
                error: false
              })
            }} className="finger" id="include-headers" type="checkbox" />
            <label className="finger" htmlFor="include-headers" >Include Headers</label>
          </div>

          <div className="form-checkbox " >
            <input defaultChecked={true} onChange={(event) => {
              this.setState({
                count_headers: event.target.checked,
                error: false
              })
            }} className="finger" id="count-header" type="checkbox" />
            <label className="finger" htmlFor="count-header" >Count Headers Row</label>
          </div>

          <div className="form-file" >
            <label>Excel File</label>
            <input
              id="file"
              type="file"
              onChange={this.onFilesAdded}
              ref={this.fileInputRef}
            />
          </div>

          <button
            className="submit-button"
            onClick={this.sendRequest}
          >Upload</button>
        </div>
      </div>
    )
  }
}

export default App
