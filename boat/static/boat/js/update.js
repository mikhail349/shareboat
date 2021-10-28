function Update() {
    const [files, setFiles] = React.useState([]);

    React.useEffect(() => {          
        loadFiles(window.boat.id);

        return () => {
            for (let file of files) {
                URL.revokeObjectURL(file.url);
            }
        }
    }, []);

    async function loadFiles(id) {
        showOverlayPanel("Загрузка...");
        try {
            let newFiles = [];
            const response = await axios.get(`/boats/api/get_files/${id}/`);
            for (let item of response.data.data) {
                let response = await fetch(item.url);
                let file = await response.blob();
                file.filename = item.filename;
                newFiles.push({
                    blob: file,
                    url: URL.createObjectURL(file)
                });
            }
            setFiles(newFiles);
        } finally {
            hideOverlayPanel();
        }
    }

    async function onDelete(e) {
        e.preventDefault();
        $('#confirmDeleteModal').modal('hide');
        try {
            await axios.post(`/boats/api/delete/${boat.id}/`);
            window.location.href = '/boats/';
        } catch(e) {
            showErrorToast((e.response.data.message || e.response.data));
        }
    }

    async function onSave(data) {   
        
        const {boat, files} = data;    

        showOverlayPanel();
        try {         
            const formData = new FormData();
            
            for (let key in boat) {
                formData.append(key, boat[key]);
            }
            
            for (let file of files) {
                formData.append('file', file.blob, file.blob.filename);
            }

            const response = await axios.post(`/boats/api/update/${boat.id}/`, formData);
            window.location.href = response.data.redirect;
        } catch (e) {       
            showErrorToast((e.response.data.message || e.response.data));
        } finally {
            hideOverlayPanel();
        }
    }

    function Buttons() {
        return (
            <div className="row g-3">
                <div className="col-auto">
                    <button type="submit" className="btn btn-outline-success">Сохранить</button>                          
                </div>
                <div className="col-auto">
                    <button type="button" className="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#confirmDeleteModal">Удалить</button>
                </div>
            </div>
        )
    }

    return (
        <>
            <BoatForm 
                files={files}
                boat={window?.boat}
                onSave={onSave}
                buttons={<Buttons />}
            />

            <div id="confirmDeleteModal" className="modal" tabindex="-1" role="dialog" aria-labelledby="confirmDeletionModalLabel" style={{display: 'none'}}>
                <div className="modal-dialog modal-dialog-centered" role="document">
                    <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title" id="confirmDeletionModalLabel">Удаление актива</h5>
                        <button type="button" className="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div className="modal-body">
                        <p>Удалить лодку?</p>
                    </div>
                    <div className="modal-footer">
                        <button id="btnConfirmDelete" type="button" className="btn btn-danger" onClick={onDelete}>Удалить</button>
                        <button type="button" className="btn btn-secondary" data-bs-dismiss="modal">Отмена</button>               
                    </div>
                    </div>
                </div>
            </div>
        </>
    )
}

ReactDOM.render(<Update />, document.querySelector('#react_app'));