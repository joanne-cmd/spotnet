import './ClosePositionModal.css';

const ClosePositionModal = ({ isOpen, onClose, closePosition, text, header, actionText }) => {
  if (!isOpen) return null;
  return (
    <div onClick={onClose} className="overlay">
      <div className="background">
        <div className="container">
          <div className="content">
            <div className="header">{header}</div>

            <div className="popup-body">
              <h3>{actionText}</h3>
              <p>{text}</p>
            </div>
          </div>
          <div className="popup-buttons">
            <button onClick={onClose} className="popup-button popup-button-cancel">
              <div className="popup-button-cancel-text">Cancel</div>
            </button>

            <button onClick={closePosition} className="popup-button popup-button-close">
              Close Active Position
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClosePositionModal;
