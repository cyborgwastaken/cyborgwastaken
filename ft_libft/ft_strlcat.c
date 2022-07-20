/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcat.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: gcyril <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2019/10/14 16:11:07 by gcyril            #+#    #+#             */
/*   Updated: 2019/11/20 13:43:43 by gcyril           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

size_t	ft_strlcat(char *dst, const char *src, size_t dstsize)
{
	unsigned int i;
	unsigned int j;
	unsigned int k;

	i = 0;
	j = 0;
	k = 0;
	i = ft_strlen(dst);
	j = ft_strlen(src);
	if (dstsize < i)
		j = j + dstsize;
	else
		j = i + j;
	while (src[k] != '\0' && i + 1 < dstsize)
	{
		dst[i++] = src[k++];
	}
	dst[i] = '\0';
	return (j);
}
