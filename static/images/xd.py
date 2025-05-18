{% extends 'base.html' %}

{% block content %}
<div class="container mt-4">
  <div class="row">

    <!-- Tabela patroli -->
    <div class="col-md-6">
      <h3>Patrole</h3>
      <table class="table table-striped">
        <thead>
          <tr>
            <th>Patrol</th>
            <th>Status</th>
            <th>Zmień status</th>
          </tr>
        </thead>
        <tbody id="patrol-table-body">
          <!-- Tu wczytane patrole -->
        </tbody>
      </table>
      <button id="logoutBtn" class="btn btn-secondary mt-3">Wyloguj się</button>
    </div>

    <!-- Komunikaty -->
    <div class="col-md-6">
      <h3>Komunikaty</h3>

      <!-- Otrzymane komunikaty -->
      <div class="mb-4">
        <h5>Otrzymane</h5>
        <div id="receivedMessages" class="border rounded p-3" style="height: 300px; overflow-y: auto; background-color: #f8f9fa;">
          <!-- Wiadomości będą tu dodawane -->
          <p class="text-muted">Brak komunikatów</p>
        </div>
      </div>

      <!-- Formularz wysyłania -->
      <div>
        <h5>Wyślij</h5>
        <form id="sendMessageForm">
          <div class="mb-3">
            <label for="patrolSelect" class="form-label">Wybierz patrol</label>
            <select class="form-select" id="patrolSelect" required>
              <!-- Opcje patroli dodane dynamicznie -->
            </select>
          </div>
          <div class="mb-3">
            <label for="messageText" class="form-label">Treść wiadomości</label>
            <textarea class="form-control" id="messageText" rows="3" required></textarea>
          </div>
          <button type="submit" class="btn btn-primary">Wyślij</button>
        </form>
      </div>
    </div>

  </div>
</div>

<script>
  document.addEventListener('DOMContentLoaded', function() {
    // Lista patroli z ich statusami - na sztywno (możesz podmienić na dynamiczne dane jeśli masz)
    const patrols = [
      { id: '601', status: 'do patrolu' },
      { id: '602', status: 'w trakcie patrolu' },
      { id: '603', status: 'do patrolu' },
      { id: '604', status: 'w trakcie patrolu' },
      { id: '605', status: 'do patrolu' },
      { id: '606', status: 'w trakcie patrolu' },
      { id: '607', status: 'do patrolu' },
      { id: '608', status: 'w trakcie patrolu' },
      { id: '609', status: 'do patrolu' },
      { id: '610', status: 'w trakcie patrolu' }
    ];

    const patrolTableBody = document.getElementById('patrol-table-body');
    const patrolSelect = document.getElementById('patrolSelect');

    // Wypełnij tabelę patroli i dropdown w formularzu komunikatów
    patrolTableBody.innerHTML = '';  // wyczyść
    patrolSelect.innerHTML = '';

    patrols.forEach(patrol => {
      // Dodaj do tabeli
      const tr = document.createElement('tr');

      // Kolumna patrol ID
      const tdId = document.createElement('td');
      tdId.textContent = patrol.id;
      tr.appendChild(tdId);

      // Kolumna status
      const tdStatus = document.createElement('td');
      tdStatus.textContent = patrol.status;
      tdStatus.classList.add('patrol-status');
      tr.appendChild(tdStatus);

      // Kolumna zmiana statusu (dropdown)
      const tdChange = document.createElement('td');
      const select = document.createElement('select');
      select.classList.add('form-select', 'form-select-sm');
      select.dataset.patrolId = patrol.id;

      // Opcje statusów
      ['do patrolu', 'w trakcie patrolu'].forEach(statusOption => {
        const option = document.createElement('option');
        option.value = statusOption;
        option.textContent = statusOption;
        if (statusOption === patrol.status) {
          option.selected = true;
        }
        select.appendChild(option);
      });

      tdChange.appendChild(select);
      tr.appendChild(tdChange);

      patrolTableBody.appendChild(tr);

      // Dodaj patrol do dropdown formularza komunikatów
      const optionForSelect = document.createElement('option');
      optionForSelect.value = patrol.id;
      optionForSelect.textContent = patrol.id;
      patrolSelect.appendChild(optionForSelect);
    });

    // Obsługa zmiany statusu patrolu
    patrolTableBody.querySelectorAll('select').forEach(selectEl => {
      selectEl.addEventListener('change', function() {
        const patrolId = this.dataset.patrolId;
        const newStatus = this.value;

        // Aktualizuj widok statusu w tabeli
        const statusTd = this.parentElement.previousElementSibling;
        statusTd.textContent = newStatus;

        // Tutaj możesz wysłać zmianę statusu do backendu (fetch POST), jeśli masz API
        console.log(`Status patrolu ${patrolId} zmieniony na: ${newStatus}`);

        // Przykład fetch (zakomentowany):
        /*
        fetch('/api/change_status/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ patrol_id: patrolId, status: newStatus })
        }).then(resp => {
          if (!resp.ok) alert('Błąd zmiany statusu');
        });
        */
      });
    });

    // Obsługa wysyłania komunikatu
    const sendForm = document.getElementById('sendMessageForm');
    sendForm.addEventListener('submit', function(e) {
      e.preventDefault();
      const patrol = patrolSelect.value;
      const message = document.getElementById('messageText').value.trim();
      if (message) {
        const receivedDiv = document.getElementById('receivedMessages');
        const noMessages = receivedDiv.querySelector('.text-muted');
        if (noMessages) noMessages.remove();

        const newMsg = document.createElement('div');
        newMsg.classList.add('alert', 'alert-info', 'mt-2');
        newMsg.textContent = `[Do patrolu ${patrol}]: ${message}`;
        receivedDiv.prepend(newMsg);

        document.getElementById('messageText').value = '';
      }
    });

    // Wylogowanie
    const logoutBtn = document.getElementById('logoutBtn');
    logoutBtn.addEventListener('click', () => {
      window.location.href = "{% url 'logout' %}";
    });
  });
</script>

{% endblock %}
