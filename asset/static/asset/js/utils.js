function FilesList(props) {
    const [count, setCount] = React.useState(0);
    const fileInputRef = React.createRef();

    function onDragEnter(e) {
        e.preventDefault();
        setCount((prevValue) => prevValue+1);
    }

    function onDragLeave(e) {
        e.preventDefault();
        setCount((prevValue) => prevValue-1);
    }

    function onDrop(e) {
        e.preventDefault();
        setCount(0);
        props.onFilesAdd(e.dataTransfer.files);
    }

    function isFileUploadHover() {
        return count > 0;
    }

    function onFileInputChange(e) {
        props.onFilesAdd(e.target.files);
        fileInputRef.current.value = null; 
    }

    return (
        <div className={`file-upload-wrapper ${isFileUploadHover() ? "bg-light" : ""}`} 
            onDragEnter={onDragEnter}
            onDragLeave={onDragLeave}
            onDrop={onDrop}
            onDragOver={(e) => e.preventDefault()}
        >    
            <div className="row">
                <input ref={fileInputRef} type="file" name="hidden_files" accept="image/*" multiple hidden onChange={onFileInputChange} />
                {
                    props.files.map((file, index) => (
                        <div key={index} className="col-md-3 mb-3">
                            <div className="card box-shadow text-end">
                                <img src={file.url} className="card-img" />  
                                <div className="card-img-overlay">
                                    <div className="btn-group">
                                        <button type="button" onClick={() => props.onFileDelete(index)} className="btn btn-sm btn-danger">
                                            Удалить
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>                    
                    ))
                }                
            </div>
            <div class="row align-items-center">
                <div class="col-auto">
                    <button type="button" className="btn btn-outline-primary" onClick={() => fileInputRef.current.click()}>
                        Добавить {!!props.files.length && 'ещё '}фото
                    </button>  
                </div> 
                <div class="col-auto">
                    {
                        isFileUploadHover() ? (
                            <span className="text-success">
                                Отпустите, чтобы добавить фото
                            </span>  
                        ) : !window.isMobile() && (
                            <span className="text-muted">
                                Или перетащите фото сюда
                            </span>     
                        )
                    }
                </div>  
            </div>
        </div>
    )
}