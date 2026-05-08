from django.views.generic.list import ListView
from django.shortcuts import render

from .models import Blog

def all_blogs(request):
    metadescription = "Temporary metadescription"

    return render(request, "main/index.html", {'metadescription': metadescription,})

class BlogsListView(ListView):
    model = Blog
    paginate_by = 12
    template_name = 'blog/bloglist.html'
    ordering = ['-publish_date']
    extra_context = { 'metacontent' : {
        'description' : 
            """Discover the latest news about space exploration and 
            technology from the perspective of passionate
            students through our SEDS blog!""",
        'author' : "",
        'keywords' : "events, SEDS, tufts, space, aerospace, astronomy"
        }
    }
    
   
def get_blog(request, slug):
    blog = Blog.objects.get(slug=slug)
    
    keywords = "tufts, Tufts, "
    # Using the tags for SEO
    for tag in blog.tags.names():
        keywords += tag + ","

    
    metacontent = {
        'description' : blog.short_description[0:150],
        'author' : blog.author.author_name,
        'keywords' : keywords,
    }

    # TODO: Create a check to see if the blog file actually exists, if it doesn't display an error on the curr
    #           page the user is on
    return render(request, "blog/blogfiles/" + blog.blog_file, {'blog': blog, 'metacontent': metacontent})