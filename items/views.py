from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Item, Claim, FoundResponse
from .forms import ItemForm, ClaimForm, SearchForm, FoundResponseForm


def is_admin(user):
    return user.is_staff


def home(request):
    form  = SearchForm(request.GET)
    items = Item.objects.filter(status='active')

    if form.is_valid():
        q         = form.cleaned_data.get('query')
        category  = form.cleaned_data.get('category')
        item_type = form.cleaned_data.get('item_type')
        date_from = form.cleaned_data.get('date_from')
        date_to   = form.cleaned_data.get('date_to')

        if q:
            items = items.filter(title__icontains=q) | items.filter(description__icontains=q)
        if category:
            items = items.filter(category=category)
        if item_type:
            items = items.filter(item_type=item_type)
        if date_from:
            items = items.filter(date_of_incident__gte=date_from)
        if date_to:
            items = items.filter(date_of_incident__lte=date_to)

    return render(request, 'items/home.html', {'items': items, 'form': form})


def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    already_claimed = False
    if request.user.is_authenticated:
        already_claimed = Claim.objects.filter(item=item, claimant=request.user).exists()
    return render(request, 'items/detail.html', {'item': item, 'already_claimed': already_claimed})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    already_claimed   = False
    already_responded = False
    if request.user.is_authenticated:
        already_claimed   = Claim.objects.filter(item=item, claimant=request.user).exists()
        already_responded = FoundResponse.objects.filter(item=item, responder=request.user).exists()
    return render(request, 'items/detail.html', {
        'item':              item,
        'already_claimed':   already_claimed,
        'already_responded': already_responded,
    })
@login_required
def mark_item_resolved(request, pk):
    item = get_object_or_404(Item, pk=pk, posted_by=request.user)
    item.status = 'resolved'
    item.save()
    messages.success(request, 'Item resolved mark ho gaya aur browse se hata diya gaya.')
    return redirect('items:dashboard')
@login_required
def post_item(request):
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.posted_by = request.user
            item.save()
            messages.success(request, 'Item posted successfully!')
            return redirect('items:detail', pk=item.pk)
    else:
        form = ItemForm()
    return render(request, 'items/post_item.html', {'form': form})


@login_required
def claim_item(request, pk):
    item = get_object_or_404(Item, pk=pk, status='active')

    if item.posted_by == request.user:
        messages.error(request, 'You cannot claim your own item.')
        return redirect('items:detail', pk=pk)

    if Claim.objects.filter(item=item, claimant=request.user).exists():
        messages.warning(request, 'You have already submitted a claim for this item.')
        return redirect('items:detail', pk=pk)

    if request.method == 'POST':
        form = ClaimForm(request.POST)
        if form.is_valid():
            claim = form.save(commit=False)
            claim.item     = item
            claim.claimant = request.user
            claim.save()
            item.status = 'claimed'
            item.save()
            messages.success(request, 'Claim submitted! You will be notified once reviewed.')
            return redirect('items:detail', pk=pk)
    else:
        form = ClaimForm()
    return render(request, 'items/claim.html', {'form': form, 'item': item})


@login_required
def dashboard(request):
    my_lost          = Item.objects.filter(posted_by=request.user, item_type='lost')
    my_found         = Item.objects.filter(posted_by=request.user, item_type='found')
    my_claims        = Claim.objects.filter(claimant=request.user)
    my_responses     = FoundResponse.objects.filter(responder=request.user)
    responses_on_my_items = FoundResponse.objects.filter(item__posted_by=request.user).order_by('-submitted_at')
    unread_count     = responses_on_my_items.filter(is_read=False).count()
    return render(request, 'dashboard/dashboard.html', {
        'my_lost':               my_lost,
        'my_found':              my_found,
        'my_claims':             my_claims,
        'my_responses':          my_responses,
        'responses_on_my_items': responses_on_my_items,
        'unread_count':          unread_count,
    })
@login_required
def found_response(request, pk):
    item = get_object_or_404(Item, pk=pk, item_type='lost', status='active')

    if item.posted_by == request.user:
        messages.error(request, 'Ye aapka apna item hai.')
        return redirect('items:detail', pk=pk)

    if FoundResponse.objects.filter(item=item, responder=request.user).exists():
        messages.warning(request, 'Aap pehle hi is item ke liye response de chuke hain.')
        return redirect('items:detail', pk=pk)

    if request.method == 'POST':
        form = FoundResponseForm(request.POST)
        if form.is_valid():
            resp = form.save(commit=False)
            resp.item      = item
            resp.responder = request.user
            resp.save()
            messages.success(request, 'Aapka message bhej diya gaya! Item owner jald contact karega.')
            return redirect('items:detail', pk=pk)
    else:
        form = FoundResponseForm()

    return render(request, 'items/found_response.html', {'form': form, 'item': item})
# ─── Admin Views ────────────────────────────────────────────

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_items    = Item.objects.count()
    active_items   = Item.objects.filter(status='active').count()
    resolved_items = Item.objects.filter(status='resolved').count()
    pending_claims = Claim.objects.filter(status='pending').count()
    all_claims     = Claim.objects.all().order_by('-submitted_at')
    all_responses  = FoundResponse.objects.all().order_by('-submitted_at')
    return render(request, 'dashboard/admin_dashboard.html', {
        'total_items':    total_items,
        'active_items':   active_items,
        'resolved_items': resolved_items,
        'pending_claims': pending_claims,
        'all_claims':     all_claims,
        'all_responses':  all_responses,
    })

@login_required
def mark_response_read(request, pk):
    resp = get_object_or_404(FoundResponse, pk=pk, item__posted_by=request.user)
    resp.is_read = True
    resp.save()
    return redirect('items:dashboard')
@login_required
@user_passes_test(is_admin)
def admin_claim_detail(request, pk):
    claim = get_object_or_404(Claim, pk=pk)
    if request.method == 'POST':
        action  = request.POST.get('action')
        remarks = request.POST.get('admin_remarks', '')
        if action == 'approve':
            claim.status        = 'approved'
            claim.admin_remarks = remarks
            claim.resolved_at   = timezone.now()
            claim.save()
            claim.item.status = 'resolved'
            claim.item.save()
            messages.success(request, f'Claim approved! Item marked as resolved.')
        elif action == 'reject':
            claim.status        = 'rejected'
            claim.admin_remarks = remarks
            claim.resolved_at   = timezone.now()
            claim.save()
            claim.item.status = 'active'
            claim.item.save()
            messages.warning(request, 'Claim rejected. Item is active again.')
        return redirect('items:admin_dashboard')
    return render(request, 'dashboard/admin_claim_detail.html', {'claim': claim})