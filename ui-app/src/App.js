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
    console.log(this.state);
    const file = this.state.docfile
    console.log(this.canUpload());
    if (!this.canUpload()) {
      this.setState({
        error: true
      });
      return;
    }

    this.setState({
      error: false
    });



    const formData = new FormData();
    formData.append("docfile", file, file.name);
    formData.append("title", this.state.title);
    formData.append("max_lines", this.state.max_lines);
    formData.append("copy_headers", this.state.copy_headers);
    formData.append("count_headers", this.state.count_headers);
    formData.append("sheet_name", this.state.sheet_name);

    const request = Axios.post("/api/document/", formData);

    request.then((e) => {
      this.setState({
        information: "Click the link below to download",
        link: e.data['data'],
        error: false
      });
    }).
      catch((e) => {
        this.setState({
          error: true
        });
      });

    // req.open("POST", "");
    // req.send(formData)

    // new Promise((resolve, reject) => {
    //   const req = new XMLHttpRequest();

    //   req.upload.addEventListener('progress', event => {
    //     if (event.lengthComputable) {
    //       const copy = { ...this.state.uploadProgress };
    //       copy[file.name] = { state: 'pending', percentage: 100 };
    //       this.setState({ uploadProgress: copy })
    //       console.log(req)
    //       resolve(req.response)
    //     }
    //   });

    //   req.upload.addEventListener('load', event => {
    //     const copy = { ...this.state.uploadProgress };
    //     copy[file.name] = { state: 'load', percentage: 100 };
    //     this.setState({ uploadProgress: copy })
    //     console.log(req)
    //     resolve(req.response)
    //   });

    //   req.upload.addEventListener('error', event => {
    //     const copy = { ...this.state.uploadProgress };
    //     copy[file.name] = { state: 'error', percentage: 0 };
    //     this.setState({ uploadProgress: copy })
    //     reject(req.response)
    //   });


    //   const formData = new FormData();
    //   formData.append("docfile", file, file.name);
    //   formData.append("title", this.state.title);
    //   formData.append("max_lines", this.state.max_lines);
    //   formData.append("copy_headers", this.state.copy_headers);
    //   formData.append("count_headers", this.state.count_headers);
    //   formData.append("sheet_name", this.state.sheet_name);

    //   req.open("POST", "http://localhost:8000/api/document/");
    //   req.send(formData)

    // }).then(function (result) {
    //   console.log(result)
    // });

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
                <a href={this.state.link}>Download File </a>
              </div>
          }
          <div className="form-input" >
            <input className="text-input" placeholder="Title" type="text" onChange={(event) => {
              this.setState({
                title: event.target.value
              });
            }} />
          </div>

          <div className="form-input" >
            <input className="text-input" placeholder="Max Lines per document" type="number" onChange={(event) => {
              this.setState({
                max_lines: event.target.value
              });
            }} />
          </div>


          <div className="form-checkbox " >
            <input defaultChecked={true} onChange={(event) => {
              this.setState({
                copy_headers: event.target.checked
              })
            }} className="finger" id="include-headers" type="checkbox" />
            <label className="finger" htmlFor="include-headers" >Include Headers</label>
          </div>

          <div className="form-checkbox " >
            <input defaultChecked={true} onChange={(event) => {
              this.setState({
                count_headers: event.target.checked
              })
            }} className="finger" id="count-header" type="checkbox" />
            <label className="finger" htmlFor="count-header" >Count Headers Row</label>
          </div>

          <div className="form-file" >
            <label>Excel File</label>
            <input
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
