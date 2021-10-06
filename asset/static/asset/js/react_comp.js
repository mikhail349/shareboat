function LikeButton() {
    const [liked, setLiked] = React.useState(false);

    if (liked) {
        return 'You liked this.';
    }
    
    return (
        <button onClick={() => setLiked(true)}>
            Like!
        </button>        
    )
}

const domContainer = document.querySelector('#app');
ReactDOM.render(<LikeButton />, domContainer);