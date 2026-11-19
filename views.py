import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.conf import settings
from .models import Resume
from apps.analysis.models import Analysis


@login_required
def dashboard_view(request):
    user = request.user
    resumes = Resume.objects.filter(user=user, is_active=True)
    analyses = Analysis.objects.filter(user=user)
    latest_analysis = analyses.first()
    recent_activity = analyses[:5]

    context = {
        'page_title': 'Dashboard',
        'total_resumes': resumes.count(),
        'total_analyses': analyses.count(),
        'latest_score': latest_analysis.ats_score if latest_analysis else None,
        'recent_activity': recent_activity,
        'resumes': resumes[:3],
    }
    return render(request, 'user/dashboard.html', context)


@login_required
def resume_list_view(request):
    resumes = Resume.objects.filter(user=request.user, is_active=True)
    return render(request, 'user/resumes.html', {
        'resumes': resumes,
        'page_title': 'My Resumes',
    })


@login_required
def upload_resume_view(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('resume_file')
        if not uploaded_file:
            messages.error(request, 'Please select a file to upload.')
            return redirect('upload_resume')

        filename = uploaded_file.name
        ext = filename.rsplit('.', 1)[-1].lower()

        if ext not in ['pdf', 'docx']:
            messages.error(request, 'Only PDF and DOCX files are supported.')
            return redirect('upload_resume')

        if uploaded_file.size > 10 * 1024 * 1024:
            messages.error(request, 'File size must be under 10 MB.')
            return redirect('upload_resume')

        resume = Resume.objects.create(
            user=request.user,
            filename=filename,
            file=uploaded_file,
            file_type=ext,
        )
        messages.success(request, f'"{filename}" uploaded successfully! You can now analyze it.')
        return redirect('resume_list')

    return render(request, 'user/upload.html', {'page_title': 'Upload Resume'})


@login_required
def delete_resume_view(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    if request.method == 'POST':
        filename = resume.filename
        try:
            if resume.file and os.path.exists(resume.file.path):
                os.remove(resume.file.path)
        except Exception:
            pass
        resume.delete()
        messages.success(request, f'"{filename}" has been deleted.')
        return redirect('resume_list')
    return render(request, 'user/confirm_delete.html', {'resume': resume, 'page_title': 'Delete Resume'})


@login_required
def download_resume_view(request, pk):
    resume = get_object_or_404(Resume, pk=pk, user=request.user)
    try:
        return FileResponse(open(resume.file.path, 'rb'),
                            as_attachment=True,
                            filename=resume.filename)
    except FileNotFoundError:
        raise Http404("Resume file not found.")
