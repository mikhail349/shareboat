function LikeButton() {
    const [files, setFiles] = React.useState([]);
    const fileInputRef = React.createRef();
    
    function onClick(e) {
        fileInputRef.current.click();
        //let newFiles = [...files];
        //newFiles.unshift("test");
        //setFiles(newFiles)
    
    }

    function onFileInputChange(e) {
        setFiles([...files, ...e.target.files]);
        fileInputRef.current.value = null;
    }

    console.log(files);

    return (
        <div className="row">
            <input ref={fileInputRef} type="file" multiple hidden onChange={onFileInputChange} />
            {
                files.map((file, index) => (
                    <div key={index} className="col-md-4">
                        <div className="card box-shadow text-center h-100" /*style={{width: "100px"}}*/>
                            <img src={URL.createObjectURL(file)} class="card-img" alt="..." />   
                        </div>
                    </div>                    
                ))
            }
            <div className="col-md-4">
                <div className="card box-shadow text-center h-100" /*style={{width: "100px"}}*/>
                    <div className="card-body align-items-center d-flex justify-content-center">
                        <div class="btn btn-primary" onClick={onClick}>Добавить фото</div>
                    </div>    
                </div>
            </div>
        </div>     
    )
}

const domContainer = document.querySelector('#react_app');
ReactDOM.render(<LikeButton />, domContainer);