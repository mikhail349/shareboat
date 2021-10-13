function FilesList() {
    const [files, setFiles] = React.useState([]);
    const fileInputRef = React.createRef();
    
    function onFileInputChange(e) {
        setFiles([...files, ...e.target.files]);
        //fileInputRef.current.value = null;
        //setFiles([...e.target.files]);
    }

    //function getFiles() {
    //    return files;
    //}

    React.useEffect(() => {
        //return () => 
    }, []);

    return (
        <React.Fragment>
            <div className={`row ${!!files.length ? 'mb-3' : ''}`}>
                <input ref={fileInputRef} type="file" name="files" multiple hidden onChange={onFileInputChange} />
                {
                    files.map((file, index) => (
                        <div key={index} className="col-md-4">
                            <div className="card box-shadow text-center h-100">
                                <img src={URL.createObjectURL(file)} class="card-img" />   
                            </div>
                        </div>                    
                    ))
                }                
            </div>
            <button id="btnAddFiles" type="button" class="btn btn-primary" onClick={() => fileInputRef.current.click()}>Добавить {!!files.length && 'ещё '}фото</button>     
        </React.Fragment>
    )
}

ReactDOM.render(<FilesList />, document.querySelector('#react_app'));