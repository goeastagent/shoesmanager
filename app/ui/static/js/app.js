// 전역 변수
let currentPage = 1;
let pageSize = 50;
let totalCount = 0;
let currentSort = 'created_at';
let currentSortDesc = true;
let selectedItemId = null;
let barcodeInputTimer = null;

// 페이지 로드 시 초기화
$(document).ready(function() {
    initializeDatepickers();
    loadFilters();
    searchItems();
    setupEventListeners();
});

// Datepicker 초기화
function initializeDatepickers() {
    $('.datepicker').datepicker({
        format: 'yyyy-mm-dd',
        language: 'ko',
        autoclose: true,
        todayHighlight: true,
        clearBtn: true
    });
    
    // 오늘 날짜를 기본값으로 설정 (새 항목 추가 시)
    $('#itemPurchaseDate').datepicker('setDate', new Date());
}

// 이벤트 리스너 설정
function setupEventListeners() {
    // 테이블 정렬
    $('.sortable').on('click', function() {
        const sortField = $(this).data('sort');
        if (currentSort === sortField) {
            currentSortDesc = !currentSortDesc;
        } else {
            currentSort = sortField;
            currentSortDesc = true;
        }
        searchItems();
    });
    
    // 엔터 키로 검색
    $('#searchForm input').on('keypress', function(e) {
        if (e.which === 13) {
            e.preventDefault();
            searchItems();
        }
    });
    
    // 바코드 입력 시 자동완성 (항목 추가/수정 모달)
    $('#itemBarcode').on('input', function() {
        clearTimeout(barcodeInputTimer);
        const barcode = $(this).val().trim();
        
        if (barcode.length >= 5) {
            barcodeInputTimer = setTimeout(() => {
                fetchBarcodeInfo(barcode);
            }, 500);
        }
    });
    
    // 판매 모달의 바코드 입력 시 엔터 키로 검색
    $('#sellBarcode').on('keypress', function(e) {
        if (e.which === 13) {
            e.preventDefault();
            searchBarcodeForSell();
        }
    });
    
    // 판매 모달이 열릴 때 바코드 필드에 포커스
    $('#sellModal').on('shown.bs.modal', function() {
        $('#sellBarcode').focus();
    });
    
    // 항목 모달이 열릴 때 바코드 필드에 포커스 (추가 모드일 때만)
    $('#itemModal').on('shown.bs.modal', function() {
        if (!$('#itemId').val()) {
            $('#itemBarcode').focus();
        }
    });
}

// 필터 옵션 로드 (위치, 구매처)
function loadFilters() {
    $.ajax({
        url: '/api/filters',
        method: 'GET',
        success: function(data) {
            // 위치 옵션
            $('#location').empty().append('<option value="">전체</option>');
            data.locations.forEach(location => {
                $('#location').append(`<option value="${location}">${location}</option>`);
            });
            
            // 구매처 옵션
            $('#vendor').empty().append('<option value="">전체</option>');
            data.vendors.forEach(vendor => {
                $('#vendor').append(`<option value="${vendor}">${vendor}</option>`);
            });
        },
        error: function(xhr) {
            console.error('필터 로드 실패:', xhr);
        }
    });
}

// 검색 실행
function searchItems(page = 1) {
    currentPage = page;
    setStatus('검색 중...');
    
    const params = {
        keyword: $('#keyword').val() || null,
        location: $('#location').val() || null,
        model_name: $('#modelName').val() || null,
        name: $('#name').val() || null,
        vendor: $('#vendor').val() || null,
        size: $('#size').val() || null,
        barcode: $('#barcode').val() || null,
        purchase_date_from: $('#purchaseDateFrom').val() || null,
        purchase_date_to: $('#purchaseDateTo').val() || null,
        sale_date_from: $('#saleDateFrom').val() || null,
        sale_date_to: $('#saleDateTo').val() || null,
        price_min: $('#priceMin').val() || null,
        price_max: $('#priceMax').val() || null,
        sort_by: currentSort,
        sort_desc: currentSortDesc,
        page: currentPage,
        page_size: pageSize
    };
    
    // null 값 제거
    Object.keys(params).forEach(key => {
        if (params[key] === null || params[key] === '') {
            delete params[key];
        }
    });
    
    $.ajax({
        url: '/api/items',
        method: 'GET',
        data: params,
        success: function(data) {
            totalCount = data.total_count;
            displayItems(data.items);
            updatePagination(data);
            updateSortIndicators();
            setStatus(`검색 완료: ${data.items.length}개 항목 (전체 ${totalCount}개)`);
        },
        error: function(xhr) {
            console.error('검색 실패:', xhr);
            setStatus('검색 실패');
            showAlert('검색에 실패했습니다.', 'danger');
        }
    });
}

// 항목 목록 표시
function displayItems(items) {
    const tbody = $('#itemTableBody');
    tbody.empty();
    
    if (items.length === 0) {
        tbody.append('<tr><td colspan="10" class="text-center text-muted">검색 결과가 없습니다.</td></tr>');
        $('#itemCount').text('0개');
        return;
    }
    
    items.forEach(item => {
        const status = item.sale_date ? '판매됨' : '재고';
        const statusClass = item.sale_date ? 'status-sold' : 'status-available';
        const saleDate = item.sale_date || '-';
        
        const row = `
            <tr data-id="${item.id}" onclick="selectItem('${item.id}')">
                <td class="text-truncate" style="max-width: 80px;" title="${item.id}">${item.id.substring(0, 8)}...</td>
                <td>${item.location}</td>
                <td>${item.purchase_date}</td>
                <td>${saleDate}</td>
                <td>${item.model_name}</td>
                <td>${item.name}</td>
                <td>${item.size || '-'}</td>
                <td class="d-none d-lg-table-cell">${item.vendor}</td>
                <td class="price-cell">₩${Number(item.price).toLocaleString()}</td>
                <td><span class="badge ${statusClass}">${status}</span></td>
            </tr>
        `;
        tbody.append(row);
    });
    
    $('#itemCount').text(`${totalCount}개`);
}

// 항목 선택
function selectItem(itemId) {
    selectedItemId = itemId;
    
    // 테이블에서 선택 표시
    $('#itemTableBody tr').removeClass('selected');
    $(`#itemTableBody tr[data-id="${itemId}"]`).addClass('selected');
    
    // 상세 정보 로드
    loadItemDetail(itemId);
}

// 상세 정보 로드
function loadItemDetail(itemId) {
    $.ajax({
        url: `/api/items/${itemId}`,
        method: 'GET',
        success: function(item) {
            const detailHtml = `
                <dl class="row">
                    <dt class="col-sm-4">ID</dt>
                    <dd class="col-sm-8 text-truncate" title="${item.id}">${item.id}</dd>
                    
                    <dt class="col-sm-4">위치</dt>
                    <dd class="col-sm-8">${item.location}</dd>
                    
                    <dt class="col-sm-4">구매일</dt>
                    <dd class="col-sm-8">${item.purchase_date}</dd>
                    
                    <dt class="col-sm-4">판매일</dt>
                    <dd class="col-sm-8">${item.sale_date || '미판매'}</dd>
                    
                    <dt class="col-sm-4">모델명</dt>
                    <dd class="col-sm-8">${item.model_name}</dd>
                    
                    <dt class="col-sm-4">제품명</dt>
                    <dd class="col-sm-8">${item.name}</dd>
                    
                    <dt class="col-sm-4">사이즈</dt>
                    <dd class="col-sm-8">${item.size || '미지정'}</dd>
                    
                    <dt class="col-sm-4">바코드</dt>
                    <dd class="col-sm-8">${item.barcode || '미지정'}</dd>
                    
                    <dt class="col-sm-4">구매처</dt>
                    <dd class="col-sm-8">${item.vendor}</dd>
                    
                    <dt class="col-sm-4">가격</dt>
                    <dd class="col-sm-8">₩${Number(item.price).toLocaleString()}</dd>
                    
                    <dt class="col-sm-4">상태</dt>
                    <dd class="col-sm-8"><span class="badge ${item.sale_date ? 'status-sold' : 'status-available'}">${item.sale_date ? '판매됨' : '재고'}</span></dd>
                    
                    <dt class="col-sm-4">메모</dt>
                    <dd class="col-sm-8">${item.notes || '없음'}</dd>
                    
                    <dt class="col-sm-4">생성일시</dt>
                    <dd class="col-sm-8">${formatDateTime(item.created_at)}</dd>
                    
                    <dt class="col-sm-4">수정일시</dt>
                    <dd class="col-sm-8">${formatDateTime(item.updated_at)}</dd>
                </dl>
            `;
            $('#detailPanel').html(detailHtml);
        },
        error: function(xhr) {
            console.error('상세 정보 로드 실패:', xhr);
            $('#detailPanel').html('<p class="text-danger text-center">상세 정보를 불러올 수 없습니다.</p>');
        }
    });
}

// 페이지네이션 업데이트
function updatePagination(data) {
    const pagination = $('#pagination');
    pagination.empty();
    
    const totalPages = Math.ceil(totalCount / pageSize);
    
    if (totalPages <= 1) {
        return;
    }
    
    // 이전 버튼
    const prevDisabled = currentPage === 1 ? 'disabled' : '';
    pagination.append(`
        <li class="page-item ${prevDisabled}">
            <a class="page-link" href="#" onclick="searchItems(${currentPage - 1}); return false;">이전</a>
        </li>
    `);
    
    // 페이지 번호
    let startPage = Math.max(1, currentPage - 2);
    let endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        pagination.append(`
            <li class="page-item">
                <a class="page-link" href="#" onclick="searchItems(1); return false;">1</a>
            </li>
        `);
        if (startPage > 2) {
            pagination.append('<li class="page-item disabled"><span class="page-link">...</span></li>');
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const active = i === currentPage ? 'active' : '';
        pagination.append(`
            <li class="page-item ${active}">
                <a class="page-link" href="#" onclick="searchItems(${i}); return false;">${i}</a>
            </li>
        `);
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            pagination.append('<li class="page-item disabled"><span class="page-link">...</span></li>');
        }
        pagination.append(`
            <li class="page-item">
                <a class="page-link" href="#" onclick="searchItems(${totalPages}); return false;">${totalPages}</a>
            </li>
        `);
    }
    
    // 다음 버튼
    const nextDisabled = currentPage === totalPages ? 'disabled' : '';
    pagination.append(`
        <li class="page-item ${nextDisabled}">
            <a class="page-link" href="#" onclick="searchItems(${currentPage + 1}); return false;">다음</a>
        </li>
    `);
}

// 정렬 인디케이터 업데이트
function updateSortIndicators() {
    $('.sortable').removeClass('sorted-asc sorted-desc');
    $(`.sortable[data-sort="${currentSort}"]`).addClass(currentSortDesc ? 'sorted-desc' : 'sorted-asc');
}

// 검색 조건 초기화
function clearSearch() {
    $('#searchForm')[0].reset();
    $('.datepicker').datepicker('clearDates');
    currentPage = 1;
    currentSort = 'created_at';
    currentSortDesc = true;
    searchItems();
}

// 새 항목 추가 모달 표시
function showAddModal() {
    $('#itemModalTitle').text('새 항목 추가');
    $('#itemForm')[0].reset();
    $('#itemId').val('');
    
    // 기본값 설정
    $('#itemLocation').val('');
    $('#itemVendor').val('');
    $('#itemPurchaseDate').datepicker('setDate', new Date());
    $('#itemSaleDate').datepicker('clearDates');
    
    const modal = new bootstrap.Modal($('#itemModal')[0]);
    modal.show();
}

// 선택한 항목 수정 모달 표시
function editSelectedItem() {
    if (!selectedItemId) {
        showAlert('수정할 항목을 선택하세요.', 'warning');
        return;
    }
    
    $.ajax({
        url: `/api/items/${selectedItemId}`,
        method: 'GET',
        success: function(item) {
            $('#itemModalTitle').text('항목 수정');
            $('#itemId').val(item.id);
            $('#itemBarcode').val(item.barcode || '');
            $('#itemLocation').val(item.location);
            $('#itemPurchaseDate').datepicker('setDate', item.purchase_date);
            if (item.sale_date) {
                $('#itemSaleDate').datepicker('setDate', item.sale_date);
            } else {
                $('#itemSaleDate').datepicker('clearDates');
            }
            $('#itemModelName').val(item.model_name);
            $('#itemName').val(item.name);
            $('#itemSize').val(item.size || '');
            $('#itemVendor').val(item.vendor);
            $('#itemPrice').val(item.price);
            $('#itemNotes').val(item.notes || '');
            
            const modal = new bootstrap.Modal($('#itemModal')[0]);
            modal.show();
        },
        error: function(xhr) {
            console.error('항목 로드 실패:', xhr);
            showAlert('항목을 불러올 수 없습니다.', 'danger');
        }
    });
}

// 항목 저장 (추가 또는 수정)
function saveItem() {
    const itemId = $('#itemId').val();
    const isEdit = !!itemId;
    
    const itemData = {
        barcode: $('#itemBarcode').val() || null,
        location: $('#itemLocation').val(),
        purchase_date: $('#itemPurchaseDate').val(),
        sale_date: $('#itemSaleDate').val() || null,
        model_name: $('#itemModelName').val(),
        name: $('#itemName').val(),
        size: $('#itemSize').val() || null,
        vendor: $('#itemVendor').val(),
        price: parseFloat($('#itemPrice').val()),
        notes: $('#itemNotes').val() || null
    };
    
    // 유효성 검사
    if (!itemData.location || !itemData.purchase_date || !itemData.model_name || 
        !itemData.name || !itemData.vendor || !itemData.price) {
        showAlert('필수 항목을 모두 입력하세요.', 'warning');
        return;
    }
    
    const url = isEdit ? `/api/items/${itemId}` : '/api/items';
    const method = isEdit ? 'PUT' : 'POST';
    
    $.ajax({
        url: url,
        method: method,
        contentType: 'application/json',
        data: JSON.stringify(itemData),
        success: function(data) {
            showAlert(`항목이 ${isEdit ? '수정' : '추가'}되었습니다.`, 'success');
            bootstrap.Modal.getInstance($('#itemModal')[0]).hide();
            searchItems(currentPage); // 현재 페이지 유지
            loadFilters(); // 필터 옵션 새로고침
        },
        error: function(xhr) {
            console.error('저장 실패:', xhr);
            const errorMsg = xhr.responseJSON?.detail || '저장에 실패했습니다.';
            showAlert(errorMsg, 'danger');
        }
    });
}

// 선택한 항목 삭제
function deleteSelectedItem() {
    if (!selectedItemId) {
        showAlert('삭제할 항목을 선택하세요.', 'warning');
        return;
    }
    
    if (!confirm('정말로 이 항목을 삭제하시겠습니까?')) {
        return;
    }
    
    $.ajax({
        url: `/api/items/${selectedItemId}`,
        method: 'DELETE',
        success: function(data) {
            showAlert('항목이 삭제되었습니다.', 'success');
            selectedItemId = null;
            $('#detailPanel').html('<p class="text-muted text-center">항목을 선택하세요.</p>');
            searchItems(currentPage); // 현재 페이지 유지
        },
        error: function(xhr) {
            console.error('삭제 실패:', xhr);
            showAlert('삭제에 실패했습니다.', 'danger');
        }
    });
}

// 판매 모달 표시
function showSellModal() {
    $('#sellBarcode').val('');
    $('#sellItemsList').html('<p class="text-muted text-center">바코드를 입력하고 검색하세요.</p>');
    const modal = new bootstrap.Modal($('#sellModal')[0]);
    modal.show();
}

// 바코드로 판매할 항목 검색
function searchBarcodeForSell() {
    const barcode = $('#sellBarcode').val().trim();
    
    if (!barcode) {
        showAlert('바코드를 입력하세요.', 'warning');
        return;
    }
    
    $.ajax({
        url: `/api/items/barcode/${barcode}`,
        method: 'GET',
        success: function(data) {
            if (data.count === 0) {
                $('#sellItemsList').html(`<p class="text-muted text-center">바코드 '${barcode}'에 해당하는 재고가 없습니다.</p>`);
                return;
            }
            
            // 재고가 1개면 바로 판매 처리
            if (data.count === 1) {
                sellItemById(data.items[0].id);
                return;
            }
            
            // 여러 개면 선택 화면 표시
            displaySellItems(data.items);
        },
        error: function(xhr) {
            console.error('바코드 검색 실패:', xhr);
            showAlert('검색에 실패했습니다.', 'danger');
        }
    });
}

// 판매할 항목 목록 표시
function displaySellItems(items) {
    let html = '<h6 class="mb-3">판매할 항목을 선택하세요:</h6>';
    
    items.forEach(item => {
        html += `
            <div class="sell-item-card" onclick="sellItemById('${item.id}')">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${item.name}</h6>
                        <p class="mb-1 text-muted small">${item.model_name}</p>
                        <p class="mb-0">
                            <span class="badge bg-secondary">${item.location}</span>
                            <span class="badge bg-info">${item.size || '사이즈 미지정'}</span>
                            <span class="badge bg-light text-dark">구매: ${item.purchase_date}</span>
                        </p>
                    </div>
                    <div class="text-end">
                        <h5 class="mb-0">₩${Number(item.price).toLocaleString()}</h5>
                        <small class="text-muted">${item.vendor}</small>
                    </div>
                </div>
            </div>
        `;
    });
    
    $('#sellItemsList').html(html);
}

// 항목 판매 처리
function sellItemById(itemId) {
    if (!confirm('이 항목을 판매 처리하시겠습니까?')) {
        return;
    }
    
    const today = new Date().toISOString().split('T')[0];
    
    $.ajax({
        url: `/api/items/${itemId}/sell`,
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ sale_date: today }),
        success: function(data) {
            showAlert('판매 처리되었습니다.', 'success');
            bootstrap.Modal.getInstance($('#sellModal')[0]).hide();
            searchItems(currentPage); // 현재 페이지 유지
        },
        error: function(xhr) {
            console.error('판매 처리 실패:', xhr);
            showAlert('판매 처리에 실패했습니다.', 'danger');
        }
    });
}

// 바코드 정보 조회 (자동완성)
function fetchBarcodeInfo(barcode) {
    $.ajax({
        url: `/api/barcode-info/${barcode}`,
        method: 'GET',
        success: function(data) {
            if (data.found) {
                // 현재 필드가 비어있을 때만 자동완성
                if (!$('#itemModelName').val()) {
                    $('#itemModelName').val(data.model_name);
                }
                if (!$('#itemName').val()) {
                    $('#itemName').val(data.name);
                }
                if (!$('#itemSize').val() && data.size) {
                    $('#itemSize').val(data.size);
                }
                if (!$('#itemPrice').val() && data.price) {
                    $('#itemPrice').val(data.price);
                }
                if (!$('#itemVendor').val() && data.vendor) {
                    $('#itemVendor').val(data.vendor);
                }
            }
        },
        error: function(xhr) {
            // 바코드 조회 실패는 무시
            console.debug('바코드 정보 없음');
        }
    });
}

// 상태 메시지 설정
function setStatus(message) {
    $('#statusText').text(message);
}

// 알림 표시
function showAlert(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    // 기존 알림 제거
    $('.alert').remove();
    
    // 새 알림 추가
    $('body').prepend(alertHtml);
    
    // 3초 후 자동 제거
    setTimeout(() => {
        $('.alert').fadeOut(300, function() {
            $(this).remove();
        });
    }, 3000);
}

// 날짜/시간 포맷
function formatDateTime(dateTimeStr) {
    if (!dateTimeStr) return '-';
    const date = new Date(dateTimeStr);
    return date.toLocaleString('ko-KR');
}

