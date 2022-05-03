
function FilesList(props) {
    const [files, setFiles] = React.useState([]);
    const [count, setCount] = React.useState(0);
    const fileInputRef = React.createRef();

    React.useEffect(() => {
        if (props.boatId) {
            loadFiles(props.boatId);
        }
    }, [])

    async function loadFiles(id) {
        const $submitBtn = $("form button[type=submit]");
        $submitBtn.attr("disabled", true);
        try {
            let newFiles = [];
            const response = await axios.get(`/boats/api/get_files/${id}/`);
            for (let item of response.data.data) {
                const response = await fetch(item.url);
                const file = await response.blob();
                file.name = item.filename;
                newFiles.push({
                    blob: file,
                    url: URL.createObjectURL(file)
                });
            }
            setFiles(newFiles);
        } finally {
            $submitBtn.attr("disabled", false);

        }
    }

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
        addFiles(e.dataTransfer.files);
    }

    function isFileUploadHover() {
        return count > 0;
    }

    function onFileInputChange(e) {
        addFiles(e.target.files);
        fileInputRef.current.value = null; 
    }

    async function addFiles(targetFiles) {
        const newFiles = [...files];
        for (let file of targetFiles) {         
            newFiles.push({
                blob: file,
                url: URL.createObjectURL(file)
            });
        }
        setFiles(newFiles);            
    }

    async function deleteFile(index) {     
        let newFiles = [...files];
        URL.revokeObjectURL(newFiles[index].url);
        newFiles.splice(index, 1);
        setFiles(newFiles);
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
                    files.map((file, index) => (
                        <div key={index} className="col-lg-3 col-md-4 mb-3">
                            <div className="card box-shadow text-end">
                                <img src={file.url} className="card-img" data-filename={file.blob.name} />  
                                <div className="card-img-overlay">
                                    <div className="btn-group">
                                        <button type="button" className="btn btn-sm btn-danger" onClick={() => deleteFile(index)}>
                                            Удалить
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>                    
                    ))
                }                
            </div>
            <div class="row row-cols-lg-auto align-items-center">
                <div class="col mb-3">
                    <button type="button" className="btn btn-outline-primary w-100" onClick={() => fileInputRef.current.click()}>
                        Добавить фото
                    </button>  
                </div> 
                {
                    !window.isMobile() && (
                        <div class="col mb-3">
                        {
                            isFileUploadHover() ? (
                                <span className="text-success">
                                    Отпустите, чтобы добавить фото
                                </span>  
                            ) : (
                                <span className="text-muted">
                                    Или перетащите фото сюда
                                </span>     
                            )
                        }
                    </div>  
                    )
                }
            </div>
        </div>
    )
}
const appPhotos = document.querySelector('#react_app_photos');
ReactDOM.render(<FilesList boatId={$(appPhotos).attr("data-boat-id")}/>, appPhotos);