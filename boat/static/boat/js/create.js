function Create() {
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

            const response = await axios.post('/boats/api/create/', formData);
            window.location.href = response.data.redirect;
        } catch (e) {
            showErrorToast((e.response.data.message || e.response.data));
        } finally {
            hideOverlayPanel();
        }
    }

    return (
        <BoatForm 
            onSave={onSave}
            buttons={<button type="submit" className="btn btn-outline-success">Сохранить</button>}
        />
    )
}

ReactDOM.render(<Create />, document.querySelector('#react_app'));